# ============================================================
# main.py — CureBay Backend Entry Point
# ============================================================
# Run with:  uvicorn main:app --host 0.0.0.0 --port 8000
# Quick setup: python setup.py
# ============================================================

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from loguru import logger
import sys

from config import settings
from database.sqlite_db import init_db
from database.vector_db import vector_db
from services.rag_service import rag_service
from services.llm_service import llm_service
from routers import auth, patients, assessment
from models.db_models import User  # noqa: F401


# ── Logging setup ─────────────────────────────────────────────
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}",
    level="DEBUG" if settings.DEBUG else "INFO",
    colorize=True,
)
logger.add(
    "logs/curebay.log",
    rotation="10 MB",
    retention="30 days",
    level="INFO",
)

STATIC_DIR = Path(__file__).resolve().parent / "static"


# ── App Lifespan ───────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=" * 60)
    logger.info(f"  {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info("  Architecture: Offline-First (No Ollama)")
    logger.info("=" * 60)

    logger.info("Step 1/4: Initialising SQLite database...")
    init_db()

    logger.info("Step 2/4: Connecting to ChromaDB vector store...")
    vector_db.connect()

    logger.info("Step 3/4: Seeding disease knowledge base...")
    try:
        count = rag_service.seed_disease_knowledge()
        logger.success(f"Disease KB ready: {count} documents.")
    except Exception as e:
        logger.error(f"Failed to seed disease KB: {e}")

    logger.info("Step 4/4: Checking LLM availability...")
    if llm_service.is_available():
        logger.success(f"LLM ready: {llm_service.get_model_name()}")
    else:
        logger.warning("MedGemma GGUF not found — will use Claude API fallback if ANTHROPIC_API_KEY is set.")
        logger.warning("Run: python setup.py  to download MedGemma (~2.7 GB)")

    logger.info("Creating default demo user...")
    from routers.auth import get_default_user
    from database.sqlite_db import SessionLocal
    db = SessionLocal()
    try:
        demo_user = get_default_user(db)
        logger.success(f"Demo user ready: {demo_user.username} (ID: {demo_user.id})")
    finally:
        db.close()

    logger.info(f"Web UI: http://localhost:8000/")
    logger.info(f"API docs: http://localhost:8000/docs")

    yield
    logger.info("CureBay backend shutting down.")


# ── FastAPI App ────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Offline-First Multimodal AI Health Assistant for Rural ASHA Workers",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(patients.router)
app.include_router(assessment.router)

# ── Static Files (Web UI) ─────────────────────────────────────
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# ── Health / Root endpoints ───────────────────────────────────
@app.get("/", tags=["UI"])
def serve_ui():
    """Serve the CureBay Web UI."""
    index = STATIC_DIR / "index.html"
    if index.exists():
        return FileResponse(str(index))
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "ui": "Place static/index.html for the web UI",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
def health_check():
    from services.embedding_service import embedding_service
    llm_ok = llm_service.is_available()
    embeddings_ok = embedding_service.is_available()
    disease_kb_count = vector_db.count(settings.VECTOR_COLLECTION_DISEASE)
    all_ok = (llm_ok or bool(settings.ANTHROPIC_API_KEY)) and embeddings_ok and disease_kb_count > 0

    return {
        "status": "healthy" if all_ok else "degraded",
        "llm": {
            "available": llm_ok,
            "model": llm_service.get_model_name(),
            "type": "MedGemma GGUF" if llm_ok else "Claude API (fallback)",
        },
        "embeddings": {
            "available": embeddings_ok,
            "model": settings.EMBEDDING_MODEL_NAME,
            "dimension": settings.EMBEDDING_DIMENSION,
        },
        "vector_store": {
            "disease_documents": disease_kb_count,
        },
        "database": "sqlite",
    }


@app.get("/setup/status", tags=["Health"])
def setup_status():
    from pathlib import Path as _Path
    from services.embedding_service import embedding_service

    medgemma_exists = _Path(settings.MEDGEMMA_MODEL_PATH).exists()
    embeddings_ok = embedding_service.is_available()
    disease_count = vector_db.count(settings.VECTOR_COLLECTION_DISEASE)
    anthropic_key = bool(settings.ANTHROPIC_API_KEY)

    return {
        "ready": disease_count > 0 and embeddings_ok,
        "models": {
            "medgemma_gguf": {
                "exists": medgemma_exists,
                "path": settings.MEDGEMMA_MODEL_PATH,
                "size": "~2.7 GB",
            },
            "claude_api_fallback": {
                "available": anthropic_key,
                "note": "Used when MedGemma is not downloaded",
            },
            "miniLM_embeddings": {
                "available": embeddings_ok,
                "model": settings.EMBEDDING_MODEL_NAME,
            },
        },
        "disease_kb_documents": disease_count,
        "sarvam_api_configured": bool(settings.SARVAM_API_KEY),
        "rppg_enabled": settings.RPPG_ENABLED,
    }


@app.get("/kb/stats", tags=["Knowledge Base"])
def kb_stats():
    return {
        "disease_knowledge": vector_db.count(settings.VECTOR_COLLECTION_DISEASE),
        "patient_contexts": vector_db.count(settings.VECTOR_COLLECTION_PATIENTS),
    }


@app.post("/kb/reseed", tags=["Knowledge Base"])
def reseed_knowledge_base():
    try:
        count = rag_service.seed_disease_knowledge(force=True)
        return {"message": f"Knowledge base re-seeded with {count} documents."}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
