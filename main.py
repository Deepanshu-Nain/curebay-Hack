# ============================================================
# main.py — CureBay Backend Entry Point
# ============================================================
# Run with:  uvicorn main:app --host 0.0.0.0 --port 8000
# Quick setup: python setup.py
#
# Architecture: Fully offline (no Ollama)
#   LLM:        MedGemma Q4_K_M GGUF via llama-cpp-python
#   Embeddings: all-MiniLM-L6-v2 via sentence-transformers
#   STT:        Sarvam AI API (online) / AI4Bharat IndicConformer (offline)
#   Vision:     EfficientNetV2-Small via torchvision
# ============================================================

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from loguru import logger
from sqlalchemy.orm import Session
import sys

from config import settings
from database.sqlite_db import init_db, get_db
from database.vector_db import vector_db
from services.rag_service import rag_service
from services.llm_service import llm_service
from models.db_models import User
from routers import auth, patients, assessment


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


# ── App Lifespan ───────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle."""
    # ── STARTUP ──────────────────────────────────────────────
    logger.info("=" * 60)
    logger.info(f"  {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info("  Architecture: Offline-First (No Ollama)")
    logger.info("=" * 60)

    # 1. Initialise SQLite database
    logger.info("Step 1/4: Initialising SQLite database...")
    init_db()

    # 2. Create demo user for testing
    logger.info("Step 2/4: Creating demo user for testing...")
    try:
        from database.sqlite_db import get_db
        from routers.auth import hash_password
        db = next(get_db())
        demo_user = db.query(User).filter(User.username == "demo").first()
        if not demo_user:
            demo_user = User(
                name="Demo Health Worker",
                username="demo",
                email="demo@curebay.local",
                phone="+919876543210",
                hashed_password=hash_password("demo123"),
                village="Demo Village",
                district="Demo District",
                state="Demo State",
                pincode="000000",
                role="ASHA",
                preferred_lang="en",
            )
            db.add(demo_user)
            db.commit()
            logger.success("Demo user created: username=demo, password=demo123")
        else:
            logger.success("Demo user already exists: username=demo, password=demo123")
        db.close()
    except Exception as e:
        logger.warning(f"Could not create demo user: {e}")

    # 3. Connect to ChromaDB vector store
    logger.info("Step 3/5: Connecting to ChromaDB vector store...")
    vector_db.connect()

    # 4. Seed disease knowledge base if not already done
    logger.info("Step 4/5: Seeding disease knowledge base (MiniLM embeddings)...")
    try:
        count = rag_service.seed_disease_knowledge()
        logger.success(f"Disease KB ready: {count} documents in vector store.")
    except Exception as e:
        logger.error(f"Failed to seed disease KB: {e}")
        logger.warning(
            "Embedding model may not be downloaded yet. "
            "It will auto-download on first use (~80 MB)."
        )

    # 5. Check MedGemma LLM availability
    logger.info("Step 5/5: Checking MedGemma LLM...")
    if llm_service.is_available():
        logger.success(f"MedGemma ready: {llm_service.get_model_name()}")
    else:
        _print_model_missing_help()

    logger.info("CureBay backend is ready.")
    logger.info(f"API docs: http://localhost:8000/docs")
    logger.info(f"Demo login: username=demo, password=demo123")
    logger.info(f"Get token: GET /demo/token or POST /auth/login")
    logger.info(f"Setup help: python setup.py --check")

    yield

    # ── SHUTDOWN ─────────────────────────────────────────────
    logger.info("CureBay backend shutting down.")


# ── Helper: print actionable setup instructions ───────────────

def _print_model_missing_help():
    """
    Print a clear, actionable message when MedGemma GGUF is missing.
    Points users to setup.py for automated download.
    """
    from pathlib import Path
    sep = "─" * 58
    print(f"\n  {sep}")
    print(f"  ⚠  MODEL NOT READY: MedGemma Q4_K_M GGUF")
    print(f"  {sep}")
    print(f"  Model file not found at:")
    print(f"    {settings.MEDGEMMA_MODEL_PATH}")
    print()
    print(f"  ▶  EASIEST FIX — run our auto-setup script:")
    print(f"       python setup.py")
    print()
    print(f"  ▶  Or download manually from HuggingFace:")
    print(f"       https://huggingface.co/unsloth/medgemma-1.5-4b-it-GGUF")
    print(f"       Save as: {settings.MEDGEMMA_MODEL_PATH}")
    print(f"  {sep}\n")


# ── FastAPI App ────────────────────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
## CureBay AI Health Assistant — Backend API

Multimodal AI-powered **fully offline** health assessment system for rural 
ASHA workers and frontline health workers in India.

### Architecture (No Ollama Required)
- **LLM**: MedGemma-1.5-4b-it Q4_K_M (GGUF, ~2.7 GB) — medical-specialised
- **Embeddings**: all-MiniLM-L6-v2 (80 MB, 384-dim) — sentence-transformers
- **Voice STT**: Sarvam AI Saaras v2 (online) / AI4Bharat IndicConformer (offline, 22 Indian languages)
- **Image**: EfficientNetV2-Small (20 MB) — torchvision
- **rPPG Vitals**: Camera-based HR/RR/SpO2 extraction (non-invasive)

### Features
- **RAG-powered diagnosis**: Retrieval Augmented Generation with disease knowledge base
- **Interactive follow-up**: AI asks clarifying questions (max 3 rounds) like a real doctor
- **Multimodal input**: Text symptoms, voice (22 Indian languages), medical images
- **Offline-capable**: Runs fully on local device — no internet or cloud dependency
- **Patient management**: Profiles, vitals tracking, assessment history
- **Risk triage**: EMERGENCY / URGENT / NORMAL classification
- **rPPG vitals**: Heart rate, respiratory rate, SpO2 from smartphone camera

### Quick Setup (Auto-Downloads Everything)
```
python setup.py
```

### Manual Setup
1. Install deps: `pip install -r requirements.txt`
2. Download MedGemma GGUF to `models/medgemma/`
3. Run: `uvicorn main:app --host 0.0.0.0 --port 8000`
""",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# ── CORS ───────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Routers ────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(patients.router)
app.include_router(assessment.router)


# ── Root / Health endpoints ────────────────────────────────────

@app.get("/", tags=["Health"])
def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "architecture": "offline-first (no Ollama)",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
def health_check():
    """System health check — useful for mobile app to verify backend connectivity."""
    from services.embedding_service import embedding_service

    llm_ok = llm_service.is_available()
    embeddings_ok = embedding_service.is_available()
    disease_kb_count = vector_db.count(settings.VECTOR_COLLECTION_DISEASE)

    all_ok = llm_ok and embeddings_ok and disease_kb_count > 0

    return {
        "status": "healthy" if all_ok else "degraded",
        "llm": {
            "available": llm_ok,
            "model": llm_service.get_model_name(),
            "type": "MedGemma GGUF (llama-cpp-python)",
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
    """
    Returns full setup status useful for first-time setup guidance.
    Mobile/web app can call this on first launch to guide users.
    """
    from pathlib import Path as _Path
    from services.embedding_service import embedding_service
    from services.voice_service import voice_service as vs
    from services.image_service import image_service as img_svc

    medgemma_exists = _Path(settings.MEDGEMMA_MODEL_PATH).exists()
    llm_ok = llm_service.is_available() if medgemma_exists else False
    embeddings_ok = embedding_service.is_available()
    disease_count = vector_db.count(settings.VECTOR_COLLECTION_DISEASE)

    ready = medgemma_exists and disease_count > 0

    return {
        "ready": ready,
        "models": {
            "medgemma_gguf": {
                "exists": medgemma_exists,
                "path": settings.MEDGEMMA_MODEL_PATH,
                "size": "~2.7 GB",
            },
            "miniLM_embeddings": {
                "available": embeddings_ok,
                "model": settings.EMBEDDING_MODEL_NAME,
                "size": "~80 MB",
            },
            "indic_conformer_stt": {
                "model": settings.INDIC_ASR_MODEL,
                "size": "~600 MB (auto-downloads on first use)",
            },
            "efficientnet_v2_s": {
                "model": settings.EFFICIENTNET_MODEL_NAME,
                "size": "~20 MB (auto-downloads on first use)",
            },
        },
        "disease_kb_documents": disease_count,
        "sarvam_api_configured": bool(settings.SARVAM_API_KEY),
        "rppg_enabled": settings.RPPG_ENABLED,
        "setup_command": "python setup.py",
        "setup_instructions": {
            "windows": "python setup.py",
            "linux_mac": "python setup.py",
        },
    }


@app.get("/kb/stats", tags=["Knowledge Base"])
def kb_stats():
    """Get knowledge base statistics."""
    return {
        "disease_knowledge": vector_db.count(settings.VECTOR_COLLECTION_DISEASE),
        "patient_contexts": vector_db.count(settings.VECTOR_COLLECTION_PATIENTS),
    }


@app.post("/kb/reseed", tags=["Knowledge Base"])
def reseed_knowledge_base(current_user=None):
    """Force re-seed the disease knowledge base (admin action)."""
    try:
        count = rag_service.seed_disease_knowledge(force=True)
        return {"message": f"Knowledge base re-seeded with {count} documents."}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# ── Demo / Testing endpoints ────────────────────────────────────

@app.get("/demo/token", tags=["Demo"], summary="Get demo user token")
def get_demo_token(db: Session = Depends(get_db)):
    """
    Get a valid JWT token for testing purposes.

    This creates a demo user if not exists and returns a token.
    Use this token in the Authorize button above (or add `Authorization: Bearer <token>` header).
    """
    from routers.auth import create_access_token, hash_password

    # Try to find or create demo user
    demo_user = db.query(User).filter(User.username == "demo").first()

    if not demo_user:
        demo_user = User(
            name="Demo Health Worker",
            username="demo",
            email="demo@curebay.local",
            phone="+919876543210",
            hashed_password=hash_password("demo123"),
            village="Demo Village",
            district="Demo District",
            state="Demo State",
            pincode="000000",
            role="ASHA",
            preferred_lang="en",
        )
        db.add(demo_user)
        db.commit()
        db.refresh(demo_user)

    token = create_access_token({"sub": demo_user.id, "role": demo_user.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "demo_username": "demo",
        "demo_password": "demo123",
        "usage": "Click 'Authorize' button above and enter: Bearer <access_token>",
    }
