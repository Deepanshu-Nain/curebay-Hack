# ============================================================
# services/embedding_service.py — Vector Embedding Service
# ============================================================
# Uses sentence-transformers `all-MiniLM-L6-v2` (80 MB) for
# dense vector embeddings. Runs fully offline in Python.
# Model produces 384-dimensional normalised vectors.
# ============================================================

from typing import List
from loguru import logger

from config import settings


class EmbeddingService:
    """Lightweight sentence-transformer embedding service (no Ollama)."""

    def __init__(self):
        self._model = None   # lazy loaded
        self._model_name = settings.EMBEDDING_MODEL_NAME

    def _load_model(self):
        """Lazy load MiniLM model on first use (saves startup memory)."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"Loading embedding model: {self._model_name}")
                self._model = SentenceTransformer(self._model_name)
                logger.success(f"Embedding model loaded: {self._model_name} ({settings.EMBEDDING_DIMENSION}-dim)")
            except ImportError:
                logger.error("sentence-transformers not installed. Run: pip install sentence-transformers")
                raise
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                raise

    def embed(self, text: str) -> List[float]:
        """
        Generate embedding for a single text string.
        Returns 384-dimensional normalised float list.
        """
        text = text.strip()
        if not text:
            raise ValueError("Cannot embed empty text.")
        try:
            self._load_model()
            embedding = self._model.encode(text, normalize_embeddings=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Embedding error: {e}")
            raise

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts efficiently.
        Uses batch encoding for better throughput.
        """
        self._load_model()
        texts = [t.strip() for t in texts if t.strip()]
        if not texts:
            return []

        try:
            embeddings = self._model.encode(
                texts,
                normalize_embeddings=True,
                batch_size=32,
                show_progress_bar=len(texts) > 20,
            )
            if (len(texts)) % 50 == 0 or len(texts) < 10:
                logger.debug(f"Embedded {len(texts)} documents")
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Batch embedding error: {e}")
            raise

    def embed_query(self, query: str) -> List[float]:
        """
        Embed a user query for similarity search.
        MiniLM doesn't differentiate query/document embeddings,
        but we keep this method for API compatibility.
        """
        return self.embed(query)

    def embed_document(self, text: str) -> List[float]:
        """Embed a document for indexing."""
        return self.embed(text)

    def is_available(self) -> bool:
        """Check if the embedding model can be loaded."""
        try:
            self._load_model()
            return True
        except Exception:
            return False


# Singleton
embedding_service = EmbeddingService()
