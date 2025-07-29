"""Embedding service for ChunkHound - manages embedding generation and caching."""

import asyncio
from typing import Any, Dict, List, Optional, Tuple
from loguru import logger

from core.types import ChunkId
from interfaces.database_provider import DatabaseProvider
from interfaces.embedding_provider import EmbeddingProvider
from .base_service import BaseService


class EmbeddingService(BaseService):
    """Service for managing embedding generation, caching, and optimization."""

    def __init__(
        self,
        database_provider: DatabaseProvider,
        embedding_provider: Optional[EmbeddingProvider] = None,
        embedding_batch_size: int = 100,
        db_batch_size: int = 500,
        max_concurrent_batches: int = 3
    ):
        """Initialize embedding service.

        Args:
            database_provider: Database provider for persistence
            embedding_provider: Embedding provider for vector generation
            embedding_batch_size: Number of texts per embedding API request
            db_batch_size: Number of records per database transaction
            max_concurrent_batches: Maximum number of concurrent embedding batches
        """
        super().__init__(database_provider)
        self._embedding_provider = embedding_provider
        self._embedding_batch_size = embedding_batch_size
        self._db_batch_size = db_batch_size
        self._max_concurrent_batches = max_concurrent_batches

    def set_embedding_provider(self, provider: EmbeddingProvider) -> None:
        """Set or update the embedding provider.

        Args:
            provider: New embedding provider implementation
        """
        self._embedding_provider = provider

    async def generate_embeddings_for_chunks(
        self,
        chunk_ids: List[ChunkId],
        chunk_texts: List[str]
    ) -> int:
        """Generate embeddings for a list of chunks.

        Args:
            chunk_ids: List of chunk IDs to generate embeddings for
            chunk_texts: Corresponding text content for each chunk

        Returns:
            Number of embeddings successfully generated
        """
        if not self._embedding_provider:
            logger.warning("No embedding provider configured")
            return 0

        if len(chunk_ids) != len(chunk_texts):
            raise ValueError("chunk_ids and chunk_texts must have the same length")

        try:
            logger.info(f"Generating embeddings for {len(chunk_ids)} chunks")

            # Filter out chunks that already have embeddings
            filtered_chunks = await self._filter_existing_embeddings(chunk_ids, chunk_texts)

            if not filtered_chunks:
                logger.info("All chunks already have embeddings")
                return 0

            # Generate embeddings in batches
            total_generated = await self._generate_embeddings_in_batches(filtered_chunks)

            logger.info(f"Successfully generated {total_generated} embeddings")
            return total_generated

        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            return 0

    async def generate_missing_embeddings(
        self,
        provider_name: Optional[str] = None,
        model_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate embeddings for all chunks that don't have them yet.

        Args:
            provider_name: Optional specific provider to generate for
            model_name: Optional specific model to generate for

        Returns:
            Dictionary with generation statistics
        """
        try:
            if not self._embedding_provider:
                return {"status": "error", "error": "No embedding provider configured", "generated": 0}

            # Use provided provider/model or fall back to configured defaults
            target_provider = provider_name or self._embedding_provider.name
            target_model = model_name or self._embedding_provider.model

            logger.info(f"Generating missing embeddings for {target_provider}/{target_model}")

            # Find chunks without embeddings
            chunks_without_embeddings = self._get_chunks_without_embeddings(target_provider, target_model)

            if not chunks_without_embeddings:
                return {"status": "complete", "generated": 0, "message": "All chunks have embeddings"}

            logger.info(f"Found {len(chunks_without_embeddings)} chunks without embeddings")

            # Extract chunk IDs and texts
            chunk_ids = [chunk["id"] for chunk in chunks_without_embeddings]
            chunk_texts = [chunk["code"] for chunk in chunks_without_embeddings]

            # Generate embeddings
            generated_count = await self.generate_embeddings_for_chunks(chunk_ids, chunk_texts)

            return {
                "status": "success",
                "generated": generated_count,
                "total_chunks": len(chunks_without_embeddings),
                "provider": target_provider,
                "model": target_model
            }

        except Exception as e:
            logger.error(f"Failed to generate missing embeddings: {e}")
            return {"status": "error", "error": str(e), "generated": 0}

    async def regenerate_embeddings(
        self,
        file_path: Optional[str] = None,
        chunk_ids: Optional[List[ChunkId]] = None
    ) -> Dict[str, Any]:
        """Regenerate embeddings for specific files or chunks.

        Args:
            file_path: Optional file path to regenerate embeddings for
            chunk_ids: Optional specific chunk IDs to regenerate

        Returns:
            Dictionary with regeneration statistics
        """
        try:
            if not self._embedding_provider:
                return {"status": "error", "error": "No embedding provider configured", "regenerated": 0}

            # Determine which chunks to regenerate
            if chunk_ids:
                chunks_to_regenerate = self._get_chunks_by_ids(chunk_ids)
            elif file_path:
                chunks_to_regenerate = self._get_chunks_by_file_path(file_path)
            else:
                return {"status": "error", "error": "Must specify either file_path or chunk_ids", "regenerated": 0}

            if not chunks_to_regenerate:
                return {"status": "complete", "regenerated": 0, "message": "No chunks found"}

            logger.info(f"Regenerating embeddings for {len(chunks_to_regenerate)} chunks")

            # Delete existing embeddings
            provider_name = self._embedding_provider.name
            model_name = self._embedding_provider.model

            chunk_ids_to_regenerate = [chunk["id"] for chunk in chunks_to_regenerate]
            self._delete_embeddings_for_chunks(chunk_ids_to_regenerate, provider_name, model_name)

            # Generate new embeddings
            chunk_texts = [chunk["code"] for chunk in chunks_to_regenerate]
            regenerated_count = await self.generate_embeddings_for_chunks(chunk_ids_to_regenerate, chunk_texts)

            return {
                "status": "success",
                "regenerated": regenerated_count,
                "total_chunks": len(chunks_to_regenerate),
                "provider": provider_name,
                "model": model_name
            }

        except Exception as e:
            logger.error(f"Failed to regenerate embeddings: {e}")
            return {"status": "error", "error": str(e), "regenerated": 0}

    def get_embedding_stats(self) -> Dict[str, Any]:
        """Get statistics about embeddings in the database.

        Returns:
            Dictionary with embedding statistics by provider and model
        """
        try:
            # Get all embedding tables
            embedding_tables = self._get_all_embedding_tables()

            if not embedding_tables:
                return {
                    "total_embeddings": 0,
                    "total_unique_chunks": 0,
                    "providers": [],
                    "configured_provider": self._embedding_provider.name if self._embedding_provider else None,
                    "configured_model": self._embedding_provider.model if self._embedding_provider else None
                }

            # Query each table and aggregate results
            all_results = []
            all_chunks = set()

            for table_name in embedding_tables:
                query = f"""
                    SELECT
                        provider,
                        model,
                        dims,
                        COUNT(*) as count,
                        COUNT(DISTINCT chunk_id) as unique_chunks
                    FROM {table_name}
                    GROUP BY provider, model, dims
                    ORDER BY provider, model, dims
                """

                table_results = self._db.execute_query(query)
                all_results.extend(table_results)

                # Get chunk IDs for total unique calculation
                chunk_query = f"SELECT provider, model, chunk_id FROM {table_name}"
                chunk_results = self._db.execute_query(chunk_query)
                all_chunks.update((row["provider"], row["model"], row["chunk_id"]) for row in chunk_results)

            # Calculate totals
            total_embeddings = sum(row["count"] for row in all_results)
            total_unique_chunks = len(all_chunks)

            return {
                "total_embeddings": total_embeddings,
                "total_unique_chunks": total_unique_chunks,
                "providers": all_results,
                "configured_provider": self._embedding_provider.name if self._embedding_provider else None,
                "configured_model": self._embedding_provider.model if self._embedding_provider else None
            }

        except Exception as e:
            logger.error(f"Failed to get embedding stats: {e}")
            return {"error": str(e)}

    async def _filter_existing_embeddings(
        self,
        chunk_ids: List[ChunkId],
        chunk_texts: List[str]
    ) -> List[Tuple[ChunkId, str]]:
        """Filter out chunks that already have embeddings.

        Args:
            chunk_ids: List of chunk IDs
            chunk_texts: Corresponding chunk texts

        Returns:
            List of (chunk_id, text) tuples for chunks without embeddings
        """
        if not self._embedding_provider:
            return []

        provider_name = self._embedding_provider.name
        model_name = self._embedding_provider.model

        # Get existing embeddings from database
        try:
            # Determine table name based on embedding dimensions
            # We need to check what dimensions this provider/model uses
            if hasattr(self._embedding_provider, 'get_dimensions'):
                dims = self._embedding_provider.get_dimensions()
            else:
                # Default to 1536 for most embedding models (OpenAI, etc.)
                dims = 1536

            table_name = f"embeddings_{dims}"

            existing_chunk_ids = self._db.get_existing_embeddings(
                chunk_ids=chunk_ids,
                provider=provider_name,
                model=model_name,
                table_name=table_name
            )
        except Exception as e:
            logger.error(f"Failed to get existing embeddings: {e}")
            existing_chunk_ids = set()

        # Filter out chunks that already have embeddings
        filtered_chunks = []
        for chunk_id, text in zip(chunk_ids, chunk_texts):
            if chunk_id not in existing_chunk_ids:
                filtered_chunks.append((chunk_id, text))

        logger.debug(f"Filtered {len(filtered_chunks)} chunks (out of {len(chunk_ids)}) need embeddings")
        return filtered_chunks

    async def _generate_embeddings_in_batches(
        self,
        chunk_data: List[Tuple[ChunkId, str]]
    ) -> int:
        """Generate embeddings for chunks in optimized batches.

        Args:
            chunk_data: List of (chunk_id, text) tuples

        Returns:
            Number of embeddings successfully generated
        """
        if not chunk_data:
            return 0

        # Create batches for embedding API requests
        batches = []
        for i in range(0, len(chunk_data), self._embedding_batch_size):
            batch = chunk_data[i:i + self._embedding_batch_size]
            batches.append(batch)

        logger.info(f"Processing {len(batches)} batches with up to {self._embedding_batch_size} chunks each")

        # Process batches with concurrency control
        semaphore = asyncio.Semaphore(self._max_concurrent_batches)

        async def process_batch(batch: List[Tuple[ChunkId, str]], batch_num: int) -> int:
            """Process a single batch of embeddings."""
            async with semaphore:
                try:
                    logger.debug(f"Processing batch {batch_num + 1}/{len(batches)} with {len(batch)} chunks")

                    # Extract chunk IDs and texts
                    chunk_ids = [chunk_id for chunk_id, _ in batch]
                    texts = [text for _, text in batch]

                    # Generate embeddings
                    if not self._embedding_provider:
                        return 0
                    embedding_results = await self._embedding_provider.embed(texts)

                    if len(embedding_results) != len(chunk_ids):
                        logger.warning(f"Batch {batch_num}: Expected {len(chunk_ids)} embeddings, got {len(embedding_results)}")
                        return 0

                    # Prepare embedding data for database
                    embeddings_data = []
                    for chunk_id, vector in zip(chunk_ids, embedding_results):
                        embeddings_data.append({
                            "chunk_id": chunk_id,
                            "provider": self._embedding_provider.name if self._embedding_provider else "unknown",
                            "model": self._embedding_provider.model if self._embedding_provider else "unknown",
                            "dims": len(vector),
                            "embedding": vector
                        })

                    # Store in database with configurable batch size
                    stored_count = self._db.insert_embeddings_batch(embeddings_data, self._db_batch_size)
                    logger.debug(f"Batch {batch_num + 1} completed: {stored_count} embeddings stored")

                    return stored_count

                except Exception as e:
                    logger.error(f"Batch {batch_num + 1} failed: {e}")
                    return 0

        # Execute all batches concurrently
        tasks = [process_batch(batch, i) for i, batch in enumerate(batches)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Count successful embeddings
        total_generated = 0
        for result in results:
            if isinstance(result, int):
                total_generated += result
            else:
                logger.error(f"Batch processing exception: {result}")

        return total_generated

    def _get_chunks_without_embeddings(self, provider: str, model: str) -> List[Dict[str, Any]]:
        """Get chunks that don't have embeddings for the specified provider/model."""
        # Get all embedding tables
        embedding_tables = self._get_all_embedding_tables()

        if not embedding_tables:
            # No embedding tables exist, return all chunks
            query = """
                SELECT c.id, c.code, c.symbol, f.path
                FROM chunks c
                JOIN files f ON c.file_id = f.id
                ORDER BY c.id
            """
            return self._db.execute_query(query)

        # Build NOT EXISTS clauses for all embedding tables
        not_exists_clauses = []
        for table_name in embedding_tables:
            not_exists_clauses.append(f"""
                NOT EXISTS (
                    SELECT 1 FROM {table_name} e
                    WHERE e.chunk_id = c.id
                    AND e.provider = ?
                    AND e.model = ?
                )
            """)

        query = f"""
            SELECT c.id, c.code, c.symbol, f.path
            FROM chunks c
            JOIN files f ON c.file_id = f.id
            WHERE {' AND '.join(not_exists_clauses)}
            ORDER BY c.id
        """

        # Parameters need to be repeated for each table
        params = [provider, model] * len(embedding_tables)
        return self._db.execute_query(query, params)

    def _get_chunks_by_ids(self, chunk_ids: List[ChunkId]) -> List[Dict[str, Any]]:
        """Get chunk data for specific chunk IDs."""
        if not chunk_ids:
            return []

        placeholders = ",".join("?" for _ in chunk_ids)
        query = f"""
            SELECT c.id, c.code, c.symbol, f.path
            FROM chunks c
            JOIN files f ON c.file_id = f.id
            WHERE c.id IN ({placeholders})
            ORDER BY c.id
        """

        return self._db.execute_query(query, chunk_ids)

    def _get_chunks_by_file_path(self, file_path: str) -> List[Dict[str, Any]]:
        """Get all chunks for a specific file path."""
        query = """
            SELECT c.id, c.code, c.symbol, f.path
            FROM chunks c
            JOIN files f ON c.file_id = f.id
            WHERE f.path = ?
            ORDER BY c.id
        """

        return self._db.execute_query(query, [file_path])

    def _delete_embeddings_for_chunks(
        self,
        chunk_ids: List[ChunkId],
        provider: str,
        model: str
    ) -> None:
        """Delete existing embeddings for specific chunks and provider/model."""
        if not chunk_ids:
            return

        # Get all embedding tables and delete from each
        embedding_tables = self._get_all_embedding_tables()

        if not embedding_tables:
            logger.debug("No embedding tables found, nothing to delete")
            return

        placeholders = ",".join("?" for _ in chunk_ids)
        deleted_count = 0

        for table_name in embedding_tables:
            query = f"""
                DELETE FROM {table_name}
                WHERE chunk_id IN ({placeholders})
                AND provider = ?
                AND model = ?
            """

            params = chunk_ids + [provider, model]
            try:
                # Execute the deletion for this table
                self._db.execute_query(query, params)
                deleted_count += 1
            except Exception as e:
                logger.error(f"Failed to delete from {table_name}: {e}")

        logger.debug(f"Deleted existing embeddings for {len(chunk_ids)} chunks from {deleted_count} tables")

    def _get_all_embedding_tables(self) -> List[str]:
        """Get list of all embedding tables (dimension-specific)."""
        try:
            tables = self._db.execute_query("""
                SELECT table_name FROM information_schema.tables
                WHERE table_name LIKE 'embeddings_%'
            """)
            return [table["table_name"] for table in tables]
        except Exception as e:
            logger.error(f"Failed to get embedding tables: {e}")
            return []
