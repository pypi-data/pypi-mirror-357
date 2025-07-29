"""Indexing coordinator service for ChunkHound - orchestrates file indexing workflows."""

from typing import Any, Dict, List, Optional, Tuple, Union
from pathlib import Path
from fnmatch import fnmatch
from loguru import logger

from core.models import File
from core.types import Language, FilePath, FileId
from interfaces.database_provider import DatabaseProvider
from interfaces.embedding_provider import EmbeddingProvider
from interfaces.language_parser import LanguageParser, ParseResult
from .base_service import BaseService


class IndexingCoordinator(BaseService):
    """Coordinates file indexing workflows with parsing, chunking, and embedding generation."""

    def __init__(
        self,
        database_provider: DatabaseProvider,
        embedding_provider: Optional[EmbeddingProvider] = None,
        language_parsers: Optional[Dict[Language, LanguageParser]] = None
    ):
        """Initialize indexing coordinator.

        Args:
            database_provider: Database provider for persistence
            embedding_provider: Optional embedding provider for vector generation
            language_parsers: Optional mapping of language to parser implementations
        """
        super().__init__(database_provider)
        self._embedding_provider = embedding_provider
        self._language_parsers = language_parsers or {}

        # Performance optimization: shared instances
        self._parser_cache: Dict[Language, LanguageParser] = {}

    def add_language_parser(self, language: Language, parser: LanguageParser) -> None:
        """Add or update a language parser.

        Args:
            language: Programming language identifier
            parser: Parser implementation for the language
        """
        self._language_parsers[language] = parser
        # Clear cache for this language
        if language in self._parser_cache:
            del self._parser_cache[language]

    def get_parser_for_language(self, language: Language) -> Optional[LanguageParser]:
        """Get parser for specified language with caching.

        Args:
            language: Programming language identifier

        Returns:
            Parser instance or None if not supported
        """
        if language not in self._parser_cache:
            if language in self._language_parsers:
                parser = self._language_parsers[language]
                # Ensure parser is initialized if setup method exists
                if hasattr(parser, 'setup') and callable(getattr(parser, 'setup')):
                    parser.setup()
                self._parser_cache[language] = parser
            else:
                return None

        return self._parser_cache[language]

    def detect_file_language(self, file_path: Path) -> Optional[Language]:
        """Detect programming language from file extension.

        Args:
            file_path: Path to the file

        Returns:
            Language enum value or None if unsupported
        """
        suffix = file_path.suffix.lower()

        language_map = {
            '.py': Language.PYTHON,
            '.java': Language.JAVA,
            '.cs': Language.CSHARP,
            '.ts': Language.TYPESCRIPT,
            '.js': Language.JAVASCRIPT,
            '.tsx': Language.TSX,
            '.jsx': Language.JSX,
            '.md': Language.MARKDOWN,
            '.markdown': Language.MARKDOWN,
            '.json': Language.JSON,
            '.yaml': Language.YAML,
            '.yml': Language.YAML,
            '.txt': Language.TEXT,
        }

        return language_map.get(suffix)

    async def process_file(self, file_path: Path, skip_embeddings: bool = False) -> Dict[str, Any]:
        """Process a single file through the complete indexing pipeline.

        Args:
            file_path: Path to the file to process
            skip_embeddings: If True, skip embedding generation for batch processing

        Returns:
            Dictionary with processing results including status, chunks, and embeddings
        """

        try:
            # Validate file exists and is readable
            if not file_path.exists() or not file_path.is_file():
                return {"status": "error", "error": f"File not found: {file_path}", "chunks": 0}

            # Detect language
            language = self.detect_file_language(file_path)
            if not language:
                return {"status": "skipped", "reason": "unsupported_type", "chunks": 0}

            # Get parser for language
            parser = self.get_parser_for_language(language)
            if not parser:
                return {"status": "error", "error": f"No parser available for {language}", "chunks": 0}

            # Get file stats for storage/update operations
            file_stat = file_path.stat()

            logger.debug(f"Processing file: {file_path}")
            logger.debug(f"File stat: mtime={file_stat.st_mtime}, size={file_stat.st_size}")

            # Note: Removed timestamp checking logic - if IndexingCoordinator.process_file() 
            # was called, the file needs processing. File watcher handles change detection.

            # Parse file content - can return ParseResult or List[Dict[str, Any]]
            parsed_data = parser.parse_file(file_path)
            if not parsed_data:
                return {"status": "no_content", "chunks": 0}

            # Extract chunks from ParseResult object or direct list
            chunks: List[Dict[str, Any]]
            if isinstance(parsed_data, ParseResult):
                # New parser providers return ParseResult object
                chunks = parsed_data.chunks
            elif isinstance(parsed_data, list):
                # Legacy parsers return chunks directly
                chunks = parsed_data
            else:
                # Fallback for unexpected types
                chunks = []

            if not chunks:
                return {"status": "no_chunks", "chunks": 0}

            # Check if this is an existing file that has been modified BEFORE storing the record
            existing_file = self._db.get_file_by_path(str(file_path))
            is_file_modified = False
            
            if existing_file:
                # Check if file was actually modified (different mtime)
                # Use same field resolution logic as process_file_incremental
                existing_mtime = 0
                current_mtime = file_stat.st_mtime
                
                if isinstance(existing_file, dict):
                    # Try different possible timestamp field names
                    for field in ['mtime', 'modified_time', 'modification_time', 'timestamp']:
                        if field in existing_file and existing_file[field] is not None:
                            timestamp_value = existing_file[field]
                            if isinstance(timestamp_value, (int, float)):
                                existing_mtime = float(timestamp_value)
                                break
                            elif hasattr(timestamp_value, "timestamp"):
                                existing_mtime = timestamp_value.timestamp()
                                break
                else:
                    # Handle File model objects
                    if hasattr(existing_file, 'mtime'):
                        existing_mtime = float(existing_file.mtime)
                
                is_file_modified = abs(current_mtime - existing_mtime) > 0.001  # Allow small float precision differences
                logger.debug(f"File modification check: {file_path} - existing_mtime: {existing_mtime}, current_mtime: {current_mtime}, modified: {is_file_modified}")

            # Store or update file record
            file_id = self._store_file_record(file_path, file_stat, language)
            if file_id is None:
                return {"status": "error", "chunks": 0, "error": "Failed to store file record"}

            # Delete old chunks only if file was actually modified
            if existing_file and is_file_modified:
                self._db.delete_file_chunks(file_id)
                logger.debug(f"Deleted existing chunks for modified file: {file_path}")

            # Store chunks and generate embeddings
            # Note: Transaction safety is handled by the database provider layer
            chunk_ids = self._store_chunks(file_id, chunks, language)
            embeddings_generated = 0
            if not skip_embeddings and self._embedding_provider and chunk_ids:
                embeddings_generated = await self._generate_embeddings(chunk_ids, chunks)

            result = {
                "status": "success",
                "file_id": file_id,
                "chunks": len(chunks),
                "chunk_ids": chunk_ids,
                "embeddings": embeddings_generated
            }

            # Include chunk data for batch processing
            if skip_embeddings:
                result["chunk_data"] = chunks

            return result

        except Exception as e:
            logger.error(f"Failed to process file {file_path}: {e}")
            return {"status": "error", "error": str(e), "chunks": 0}

    async def _process_file_modification_safe(
        self,
        file_id: int,
        file_path: Path,
        file_stat,
        chunks: List[Dict[str, Any]],
        language: Language,
        skip_embeddings: bool
    ) -> Tuple[List[int], int]:
        """Process file modification with transaction safety to prevent data loss.

        This method ensures that old content is preserved if new content processing fails.
        Uses database transactions and backup tables for rollback capability.

        Args:
            file_id: Existing file ID in database
            file_path: Path to the file being processed
            file_stat: File stat object with mtime and size
            chunks: New chunks to store
            language: File language type
            skip_embeddings: Whether to skip embedding generation

        Returns:
            Tuple of (chunk_ids, embeddings_generated)

        Raises:
            Exception: If transaction-safe processing fails and rollback is needed
        """
        import time

        logger.debug(f"Transaction-safe processing - Starting for file_id: {file_id}")

        # Create unique backup table names using timestamp
        timestamp = int(time.time() * 1000000)  # microseconds for uniqueness
        chunks_backup_table = f"chunks_backup_{timestamp}"
        embeddings_backup_table = f"embeddings_1536_backup_{timestamp}"

        connection = self._db.connection
        if connection is None:
            raise RuntimeError("Database connection not available")

        try:
            # Start transaction
            connection.execute("BEGIN TRANSACTION")
            logger.debug(f"Transaction-safe processing - Transaction started")

            # Get count of existing chunks for reporting
            existing_chunks_count = connection.execute(
                "SELECT COUNT(*) FROM chunks WHERE file_id = ?", [file_id]
            ).fetchone()[0]
            logger.debug(f"Transaction-safe processing - Found {existing_chunks_count} existing chunks")

            # Create backup table for chunks
            connection.execute(f"""
                CREATE TABLE {chunks_backup_table} AS
                SELECT * FROM chunks WHERE file_id = ?
            """, [file_id])
            logger.debug(f"Transaction-safe processing - Created backup table: {chunks_backup_table}")

            # Create backup table for embeddings
            connection.execute(f"""
                CREATE TABLE {embeddings_backup_table} AS
                SELECT e.* FROM embeddings_1536 e
                JOIN chunks c ON e.chunk_id = c.id
                WHERE c.file_id = ?
            """, [file_id])
            logger.debug(f"Transaction-safe processing - Created embedding backup: {embeddings_backup_table}")

            # Update file metadata first
            self._db.update_file(file_id, size_bytes=file_stat.st_size, mtime=file_stat.st_mtime)

            # Remove old content (but backup preserved in transaction)
            self._db.delete_file_chunks(file_id)
            logger.debug(f"Transaction-safe processing - Removed old content")

            # Store new chunks
            chunk_ids = self._store_chunks(file_id, chunks, language)
            if not chunk_ids:
                raise Exception("Failed to store new chunks")
            logger.debug(f"Transaction-safe processing - Stored {len(chunk_ids)} new chunks")

            # Generate embeddings if requested
            embeddings_generated = 0
            if not skip_embeddings and self._embedding_provider and chunk_ids:
                embeddings_generated = await self._generate_embeddings(chunk_ids, chunks, connection)
                logger.debug(f"Transaction-safe processing - Generated {embeddings_generated} embeddings")

            # Commit transaction
            connection.execute("COMMIT")
            logger.debug(f"Transaction-safe processing - Transaction committed successfully")

            # Cleanup backup tables
            try:
                connection.execute(f"DROP TABLE {chunks_backup_table}")
                connection.execute(f"DROP TABLE {embeddings_backup_table}")
                logger.debug(f"Transaction-safe processing - Backup tables cleaned up")
            except Exception as cleanup_error:
                logger.warning(f"Failed to cleanup backup tables: {cleanup_error}")

            return chunk_ids, embeddings_generated

        except Exception as e:
            logger.error(f"Transaction-safe processing failed: {e}")

            try:
                # Rollback transaction
                connection.execute("ROLLBACK")
                logger.debug(f"Transaction-safe processing - Transaction rolled back")

                # Restore from backup tables if they exist
                try:
                    # Check if backup tables still exist
                    backup_exists = connection.execute(f"""
                        SELECT COUNT(*) FROM sqlite_master
                        WHERE type='table' AND name='{chunks_backup_table}'
                    """).fetchone()[0] > 0

                    if backup_exists:
                        # Restore chunks from backup
                        connection.execute(f"""
                            INSERT INTO chunks SELECT * FROM {chunks_backup_table}
                        """)

                        # Restore embeddings from backup
                        connection.execute(f"""
                            INSERT INTO embeddings_1536 SELECT * FROM {embeddings_backup_table}
                        """)

                        logger.info(f"Transaction-safe processing - Original content restored from backup")

                        # Cleanup backup tables
                        connection.execute(f"DROP TABLE {chunks_backup_table}")
                        connection.execute(f"DROP TABLE {embeddings_backup_table}")

                except Exception as restore_error:
                    logger.error(f"Failed to restore from backup: {restore_error}")

            except Exception as rollback_error:
                logger.error(f"Failed to rollback transaction: {rollback_error}")

            # Re-raise the original exception
            raise e

    async def process_directory(
        self,
        directory: Path,
        patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Process all supported files in a directory with batch optimization.

        Args:
            directory: Directory path to process
            patterns: Optional file patterns to include
            exclude_patterns: Optional file patterns to exclude

        Returns:
            Dictionary with processing statistics
        """
        try:
            # Discover files
            files = self._discover_files(directory, patterns, exclude_patterns)

            if not files:
                return {"status": "no_files", "files_processed": 0, "total_chunks": 0}

            # Process files in batches for optimal performance
            total_files = 0
            total_chunks = 0
            total_embeddings = 0

            # First pass: process files without embeddings for batch optimization
            file_chunks_for_embedding = []

            for file_path in files:
                result = await self.process_file(file_path, skip_embeddings=True)

                if result["status"] == "success":
                    total_files += 1
                    total_chunks += result["chunks"]

                    # Collect chunks for batch embedding generation
                    if "chunk_data" in result:
                        file_chunks_for_embedding.extend([
                            (chunk_id, chunk_data)
                            for chunk_id, chunk_data in zip(result["chunk_ids"], result["chunk_data"])
                        ])

            # Second pass: generate embeddings in batches
            if self._embedding_provider and file_chunks_for_embedding:
                total_embeddings = await self._generate_embeddings_batch(file_chunks_for_embedding)

            return {
                "status": "success",
                "files_processed": total_files,
                "total_chunks": total_chunks,
                "total_embeddings": total_embeddings
            }

        except Exception as e:
            logger.error(f"Failed to process directory {directory}: {e}")
            return {"status": "error", "error": str(e)}

    def _extract_file_id(self, file_record: Union[Dict[str, Any], File]) -> Optional[int]:
        """Safely extract file ID from either dict or File model."""
        if isinstance(file_record, File):
            return file_record.id
        elif isinstance(file_record, dict) and "id" in file_record:
            return file_record["id"]
        else:
            return None


    def _store_file_record(self, file_path: Path, file_stat: Any, language: Language) -> int:
        """Store or update file record in database."""
        # Check if file already exists
        existing_file = self._db.get_file_by_path(str(file_path))

        if existing_file:
            # Update existing file with new metadata
            if isinstance(existing_file, dict) and "id" in existing_file:
                file_id = existing_file["id"]
                self._db.update_file(file_id, size_bytes=file_stat.st_size, mtime=file_stat.st_mtime)
                return file_id

        # Create new File model instance
        file_model = File(
            path=FilePath(str(file_path)),
            size_bytes=file_stat.st_size,
            mtime=file_stat.st_mtime,
            language=language
        )
        return self._db.insert_file(file_model)

    def _store_chunks(self, file_id: int, chunks: List[Dict[str, Any]], language: Language) -> List[int]:
        """Store chunks in database and return chunk IDs."""
        chunk_ids = []
        for chunk in chunks:
            # Skip chunks with empty code content to prevent validation errors
            code_content = chunk.get("code", "")
            if not code_content or not code_content.strip():
                logger.warning(f"Skipping chunk with empty code content: {chunk.get('symbol', 'unknown')} at lines {chunk.get('start_line', 0)}-{chunk.get('end_line', 0)}")
                continue

            # Create Chunk model instance
            from core.models import Chunk
            from core.types import ChunkType

            # Convert chunk_type string to enum
            chunk_type_str = chunk.get("chunk_type", "function")
            try:
                chunk_type_enum = ChunkType(chunk_type_str)
            except ValueError:
                chunk_type_enum = ChunkType.FUNCTION  # default fallback

            chunk_model = Chunk(
                file_id=FileId(file_id),
                symbol=chunk.get("symbol", ""),
                start_line=chunk.get("start_line", 0),
                end_line=chunk.get("end_line", 0),
                code=code_content,
                chunk_type=chunk_type_enum,
                language=language,  # Use the file's detected language
                parent_header=chunk.get("parent_header")
            )
            chunk_id = self._db.insert_chunk(chunk_model)
            chunk_ids.append(chunk_id)
        return chunk_ids

    async def get_stats(self) -> Dict[str, Any]:
        """Get database statistics.

        Returns:
            Dictionary with file, chunk, and embedding counts
        """
        return self._db.get_stats()

    async def remove_file(self, file_path: str) -> int:
        """Remove a file and all its chunks from the database.

        Args:
            file_path: Path to the file to remove

        Returns:
            Number of chunks removed
        """
        try:
            # Get file record to get chunk count before deletion
            file_record = self._db.get_file_by_path(file_path)
            if not file_record:
                return 0

            # Get file ID
            file_id = self._extract_file_id(file_record)
            if file_id is None:
                return 0

            # Count chunks before deletion
            chunks = self._db.get_chunks_by_file_id(file_id)
            chunk_count = len(chunks) if chunks else 0

            # Delete the file completely (this will also delete chunks and embeddings)
            success = self._db.delete_file_completely(file_path)
            return chunk_count if success else 0

        except Exception as e:
            logger.error(f"Failed to remove file {file_path}: {e}")
            return 0

    async def generate_missing_embeddings(self) -> Dict[str, Any]:
        """Generate embeddings for chunks that don't have them.

        Returns:
            Dictionary with generation results
        """
        if not self._embedding_provider:
            return {"status": "error", "error": "No embedding provider configured", "generated": 0}

        try:
            # Use EmbeddingService for embedding generation
            from .embedding_service import EmbeddingService

            embedding_service = EmbeddingService(
                database_provider=self._db,
                embedding_provider=self._embedding_provider
            )

            return await embedding_service.generate_missing_embeddings()

        except Exception as e:
            logger.error(f"Failed to generate missing embeddings: {e}")
            return {"status": "error", "error": str(e), "generated": 0}

    async def _generate_embeddings(self, chunk_ids: List[int], chunks: List[Dict[str, Any]], connection=None) -> int:
        """Generate embeddings for chunks."""
        logger.info(f"SEMANTIC_DEBUG: _generate_embeddings called for {len(chunk_ids)} chunks")
        logger.info(f"SEMANTIC_DEBUG: embedding_provider available: {self._embedding_provider is not None}")

        if not self._embedding_provider:
            logger.info(f"SEMANTIC_DEBUG: No embedding provider - returning 0")
            return 0

        try:
            # Extract text content for embedding
            texts = [chunk.get("code", "") for chunk in chunks]

            # Generate embeddings
            embedding_results = await self._embedding_provider.embed(texts)

            # Store embeddings in database
            embeddings_data = []
            for chunk_id, vector in zip(chunk_ids, embedding_results):
                embeddings_data.append({
                    "chunk_id": chunk_id,
                    "provider": self._embedding_provider.name,
                    "model": self._embedding_provider.model,
                    "dims": len(vector),
                    "embedding": vector
                })

            # Database storage - use provided connection for transaction context
            result = self._db.insert_embeddings_batch(embeddings_data, connection=connection)

            logger.info(f"SEMANTIC_DEBUG: Successfully generated {result} embeddings")
            return result

        except Exception as e:
            logger.error(f"SEMANTIC_DEBUG: Failed to generate embeddings: {e}")
            logger.error(f"Failed to generate embeddings: {e}")
            return 0

    async def _generate_embeddings_batch(self, file_chunks: List[Tuple[int, Dict[str, Any]]]) -> int:
        """Generate embeddings for chunks in optimized batches."""
        if not self._embedding_provider or not file_chunks:
            return 0

        # Extract chunk IDs and text content
        chunk_ids = [chunk_id for chunk_id, _ in file_chunks]
        chunks = [chunk_data for _, chunk_data in file_chunks]

        return await self._generate_embeddings(chunk_ids, chunks)

    def _discover_files(
        self,
        directory: Path,
        patterns: Optional[List[str]],
        exclude_patterns: Optional[List[str]]
    ) -> List[Path]:
        """Discover files in directory matching patterns."""
        files = []

        # Default patterns for supported languages
        if not patterns:
            patterns = ["*.py", "*.java", "*.cs", "*.ts", "*.js", "*.tsx", "*.jsx", "*.md", "*.markdown"]

        # Default exclude patterns
        if not exclude_patterns:
            exclude_patterns = ["*/__pycache__/*", "*/node_modules/*", "*/.git/*", "*/venv/*", "*/.venv/*"]

        for pattern in patterns:
            for file_path in directory.rglob(pattern):
                if file_path.is_file():
                    # Check exclude patterns using proper fnmatch against both absolute and relative paths
                    should_exclude = False
                    rel_path = file_path.relative_to(directory)

                    for exclude_pattern in exclude_patterns:
                        # Test both relative path and absolute path for pattern matching
                        if (fnmatch(str(rel_path), exclude_pattern) or
                            fnmatch(str(file_path), exclude_pattern)):
                            should_exclude = True
                            break

                    if not should_exclude:
                        files.append(file_path)

        return sorted(files)
