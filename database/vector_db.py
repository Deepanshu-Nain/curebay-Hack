# ============================================================
# database/vector_db.py — ChromaDB Vector Store Wrapper
# ============================================================
# Persistent local ChromaDB for semantic search.
# Stores disease knowledge embeddings and patient context
# vectors for RAG retrieval.
# ============================================================

from typing import List, Dict, Any, Optional
from loguru import logger

from config import settings


class VectorDB:
    """Wrapper around ChromaDB for CureBay vector operations."""

    def __init__(self):
        self._client = None
        self._collections: Dict[str, Any] = {}
        self._collection_aliases: Dict[str, str] = {}

    def connect(self):
        """Initialise persistent ChromaDB client."""
        try:
            import chromadb
            from chromadb.config import Settings as ChromaSettings

            self._client = chromadb.PersistentClient(
                path=settings.CHROMA_PERSIST_DIR,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True,
                ),
            )
            logger.success(f"ChromaDB connected: {settings.CHROMA_PERSIST_DIR}")
        except ImportError:
            logger.error("chromadb not installed. Run: pip install chromadb")
            raise
        except Exception as e:
            logger.error(f"ChromaDB connection failed: {e}")
            raise

    def _resolve_collection_name(self, logical_name: str) -> str:
        """
        Map logical collection names to physical names.

        Embedding vectors are dimension-specific in ChromaDB, so we namespace
        key collections by embedding dimension to avoid legacy mismatch errors.
        """
        if logical_name in self._collection_aliases:
            return self._collection_aliases[logical_name]

        dim_scoped = {
            settings.VECTOR_COLLECTION_DISEASE,
            settings.VECTOR_COLLECTION_PATIENTS,
        }
        if logical_name in dim_scoped:
            physical_name = f"{logical_name}_d{settings.EMBEDDING_DIMENSION}"
        else:
            physical_name = logical_name

        self._collection_aliases[logical_name] = physical_name
        return physical_name

    def _get_collection(self, logical_name: str):
        """Get or create a collection (cached)."""
        physical_name = self._resolve_collection_name(logical_name)

        if physical_name not in self._collections:
            self._collections[physical_name] = self._client.get_or_create_collection(
                name=physical_name,
                metadata={"hnsw:space": "cosine"},  # cosine similarity
            )
            logger.info(f"Using Chroma collection '{logical_name}' -> '{physical_name}'")
        return self._collections[physical_name]

    def upsert(
        self,
        collection_name: str,
        ids: List[str],
        embeddings: List[List[float]],
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ):
        """Insert or update documents with their embeddings."""
        collection = self._get_collection(collection_name)
        # ChromaDB has a batch limit — process in chunks of 100
        batch_size = 100
        for i in range(0, len(ids), batch_size):
            end = min(i + batch_size, len(ids))
            batch_kwargs = {
                "ids": ids[i:end],
                "embeddings": embeddings[i:end],
                "documents": documents[i:end],
            }
            if metadatas:
                batch_kwargs["metadatas"] = metadatas[i:end]
            collection.upsert(**batch_kwargs)
        logger.debug(f"Upserted {len(ids)} docs into '{collection_name}'")

    def query(
        self,
        collection_name: str,
        query_embeddings: List[List[float]],
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Query collection by embedding similarity."""
        collection = self._get_collection(collection_name)
        kwargs = {
            "query_embeddings": query_embeddings,
            "n_results": n_results,
            "include": ["documents", "metadatas", "distances"],
        }
        if where:
            kwargs["where"] = where
        return collection.query(**kwargs)

    def delete(self, collection_name: str, ids: List[str]):
        """Delete documents by IDs."""
        collection = self._get_collection(collection_name)
        collection.delete(ids=ids)
        logger.debug(f"Deleted {len(ids)} docs from '{collection_name}'")

    def count(self, collection_name: str) -> int:
        """Get document count in a collection."""
        try:
            collection = self._get_collection(collection_name)
            return collection.count()
        except Exception:
            return 0

    def collection_exists_and_populated(self, collection_name: str) -> bool:
        """Check if a collection exists and has documents."""
        try:
            return self.count(collection_name) > 0
        except Exception:
            return False


# Singleton
vector_db = VectorDB()
