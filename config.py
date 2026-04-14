# ============================================================
# config.py — CureBay Application Configuration
# ============================================================
# Centralised settings using Pydantic BaseSettings.
# All values can be overridden via environment variables or .env file.
#
# Architecture: Fully offline — no Ollama dependency.
#   LLM:        MedGemma Q4_K_M GGUF via llama-cpp-python
#   Embeddings: all-MiniLM-L6-v2 via sentence-transformers
#   STT:        Sarvam AI API (online) / AI4Bharat IndicConformer (offline)
#   Vision:     EfficientNetV2-Small via torchvision
# ============================================================

from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field


BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    """Application-wide configuration."""

    # ── App ────────────────────────────────────────────────────
    APP_NAME: str = "CureBay AI Health Assistant"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = True

    # ── Security / JWT ─────────────────────────────────────────
    SECRET_KEY: str = "curebay-super-secret-key-change-in-production-2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours (offline use)

    # ── SQLite Database ────────────────────────────────────────
    SQLITE_DB_PATH: str = str(BASE_DIR / "curebay.db")
    SQLALCHEMY_DATABASE_URL: str = Field(default="")

    # ── MedGemma LLM (GGUF via llama-cpp-python) ──────────────
    MEDGEMMA_MODEL_PATH: str = str(BASE_DIR / "models" / "medgemma" / "medgemma-1.5-4b-it-Q4_K_M.gguf")
    MEDGEMMA_N_CTX: int = 2048          # context window size
    MEDGEMMA_N_GPU_LAYERS: int = 0      # 0 = CPU-only (safe for Android/low-spec)
    MEDGEMMA_TEMPERATURE: float = 0.2
    MEDGEMMA_MAX_TOKENS: int = 1500

    # ── Sentence Embeddings (MiniLM) ──────────────────────────
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384

    # ── ChromaDB (Vector Store) ────────────────────────────────
    CHROMA_PERSIST_DIR: str = str(BASE_DIR / "chroma_data")
    VECTOR_COLLECTION_DISEASE: str = "disease_knowledge"
    VECTOR_COLLECTION_PATIENTS: str = "patient_contexts"

    # ── RAG Parameters ─────────────────────────────────────────
    RAG_TOP_K: int = 5              # number of chunks to retrieve
    RAG_SIMILARITY_THRESHOLD: float = 0.35  # minimum cosine similarity

    # ── Sarvam AI Voice (online STT) ──────────────────────────
    SARVAM_API_KEY: str = ""              # empty = offline-only mode
    SARVAM_API_URL: str = "https://api.sarvam.ai/speech-to-text"
    SARVAM_LANGUAGE_CODE: str = "hi-IN"

    # ── AI4Bharat IndicConformer (offline STT) ────────────────
    INDIC_ASR_MODEL: str = "ai4bharat/indicconformer_stt_hi_hybrid_rnnt_large"

    # ── EfficientNetV2 Image Classification ───────────────────
    EFFICIENTNET_MODEL_NAME: str = "efficientnet_v2_s"
    EFFICIENTNET_WEIGHTS: str = "DEFAULT"

    # ── rPPG Vital Signs ──────────────────────────────────────
    RPPG_ENABLED: bool = True
    RPPG_FPS: int = 30
    RPPG_WINDOW_SECONDS: int = 15

    # ── Interactive Follow-up Loop ────────────────────────────
    MAX_FOLLOWUP_ROUNDS: int = 3
    FOLLOWUP_CONFIDENCE_THRESHOLD: float = 0.6  # below this → ask follow-ups

    # ── File Uploads ───────────────────────────────────────────
    UPLOADS_DIR: Path = BASE_DIR / "uploads"
    MAX_UPLOAD_SIZE_MB: int = 20

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    def model_post_init(self, __context):
        """Compute derived settings and create directories."""
        if not self.SQLALCHEMY_DATABASE_URL:
            self.SQLALCHEMY_DATABASE_URL = f"sqlite:///{self.SQLITE_DB_PATH}"

        # Ensure directories exist
        self.UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
        Path(self.CHROMA_PERSIST_DIR).mkdir(parents=True, exist_ok=True)
        (BASE_DIR / "logs").mkdir(parents=True, exist_ok=True)
        (BASE_DIR / "models" / "medgemma").mkdir(parents=True, exist_ok=True)


settings = Settings()
