# ============================================================
# database/sqlite_db.py — SQLAlchemy Engine & Session
# ============================================================
# Lightweight SQLite backend — no server needed, single file.
# Perfect for offline deployment on low-spec devices.
# ============================================================

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from loguru import logger

from config import settings

# ── Engine ─────────────────────────────────────────────────────
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite needs this for FastAPI
    echo=settings.DEBUG,
)

# ── Session factory ────────────────────────────────────────────
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ── Declarative base ──────────────────────────────────────────
Base = declarative_base()


def get_db():
    """
    FastAPI dependency — yields a database session.
    Ensures the session is closed after each request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Create all tables defined in models.
    Safe to call multiple times — only creates if not exists.
    """
    from models.db_models import User, Patient, VitalRecord, Assessment  # noqa: F401
    Base.metadata.create_all(bind=engine)
    logger.success(f"SQLite database initialised: {settings.SQLITE_DB_PATH}")
