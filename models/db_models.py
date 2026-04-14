# ============================================================
# models/db_models.py — SQLAlchemy ORM Models
# ============================================================
# All database tables for CureBay:
#   - User (health workers: ASHA, ANM, doctors)
#   - Patient (registered patients)
#   - VitalRecord (vital sign measurements)
#   - Assessment (AI health assessment results)
# ============================================================

import uuid
import enum
from datetime import datetime, timezone

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text, DateTime,
    ForeignKey, Enum as SQLEnum
)
from sqlalchemy.orm import relationship

from database.sqlite_db import Base


# ── Enums ──────────────────────────────────────────────────────

class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class InputType(str, enum.Enum):
    TEXT = "text"
    VOICE = "voice"
    IMAGE = "image"
    MIXED = "mixed"


class RiskLevel(str, enum.Enum):
    EMERGENCY = "EMERGENCY"
    URGENT = "URGENT"
    NORMAL = "NORMAL"


class UserRole(str, enum.Enum):
    ASHA = "asha"
    ANM = "anm"
    DOCTOR = "doctor"
    ADMIN = "admin"


# ── Helper ─────────────────────────────────────────────────────

def _generate_id():
    return str(uuid.uuid4())


def _utc_now():
    return datetime.now(timezone.utc)


# ── User ───────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=_generate_id)
    name = Column(String(100), nullable=False)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=True)
    phone = Column(String(15), nullable=True)
    hashed_password = Column(String(128), nullable=False)

    # Location
    village = Column(String(100), nullable=True)
    district = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    pincode = Column(String(10), nullable=True)

    # Role & preferences
    role = Column(String(20), default=UserRole.ASHA.value)
    preferred_lang = Column(String(5), default="en")

    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=_utc_now)
    updated_at = Column(DateTime, default=_utc_now, onupdate=_utc_now)

    # Relationships
    patients = relationship("Patient", back_populates="registered_by", lazy="dynamic")


# ── Patient ────────────────────────────────────────────────────

class Patient(Base):
    __tablename__ = "patients"

    id = Column(String, primary_key=True, default=_generate_id)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(10), nullable=False)  # stored as string from Gender enum
    phone = Column(String(15), nullable=True)

    # Location
    village = Column(String(100), nullable=True)
    district = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)

    # Medical history (stored as JSON strings)
    known_conditions = Column(Text, default="[]")     # JSON array
    current_medications = Column(Text, default="[]")   # JSON array
    allergies = Column(Text, nullable=True)

    # Physical
    weight_kg = Column(Float, nullable=True)
    height_cm = Column(Float, nullable=True)
    blood_group = Column(String(10), nullable=True)

    # Registered by which health worker
    registered_by_id = Column(String, ForeignKey("users.id"), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=_utc_now)
    updated_at = Column(DateTime, default=_utc_now, onupdate=_utc_now)

    # Relationships
    registered_by = relationship("User", back_populates="patients")
    vitals = relationship("VitalRecord", back_populates="patient", lazy="dynamic",
                          cascade="all, delete-orphan")
    assessments = relationship("Assessment", back_populates="patient", lazy="dynamic",
                               cascade="all, delete-orphan")


# ── Vital Record ──────────────────────────────────────────────

class VitalRecord(Base):
    __tablename__ = "vital_records"

    id = Column(String, primary_key=True, default=_generate_id)
    patient_id = Column(String, ForeignKey("patients.id"), nullable=False, index=True)

    # Vital signs
    temperature_c = Column(Float, nullable=True)      # body temperature (°C)
    bp_systolic = Column(Integer, nullable=True)       # blood pressure systolic (mmHg)
    bp_diastolic = Column(Integer, nullable=True)      # blood pressure diastolic (mmHg)
    pulse_bpm = Column(Integer, nullable=True)         # pulse rate (beats/min)
    spo2_pct = Column(Float, nullable=True)            # oxygen saturation (%)
    blood_glucose = Column(Float, nullable=True)       # blood glucose (mg/dL)
    rr_per_min = Column(Integer, nullable=True)        # respiratory rate (/min)
    weight_kg = Column(Float, nullable=True)           # weight at time of recording
    notes = Column(Text, nullable=True)                # additional observations

    # Timestamp
    recorded_at = Column(DateTime, default=_utc_now)

    # Relationship
    patient = relationship("Patient", back_populates="vitals")


# ── Assessment ─────────────────────────────────────────────────

class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(String, primary_key=True, default=_generate_id)
    patient_id = Column(String, ForeignKey("patients.id"), nullable=False, index=True)

    # Input
    input_type = Column(SQLEnum(InputType), default=InputType.TEXT)
    symptoms_text = Column(Text, nullable=False)       # transcribed or typed symptoms
    image_path = Column(String(500), nullable=True)    # path to uploaded image
    voice_path = Column(String(500), nullable=True)    # path to uploaded audio

    # AI output
    possible_conditions = Column(Text, default="[]")   # JSON array of conditions
    risk_level = Column(SQLEnum(RiskLevel), default=RiskLevel.NORMAL)
    risk_reason = Column(Text, nullable=True)
    next_steps = Column(Text, default="[]")            # JSON array of actions
    patient_summary = Column(Text, nullable=True)      # structured summary for referral

    # RAG metadata
    retrieved_chunks = Column(Text, default="[]")      # JSON — which KB docs were used
    model_used = Column(String(50), nullable=True)
    confidence = Column(Float, default=0.5)

    # Timestamp
    created_at = Column(DateTime, default=_utc_now)

    # Relationship
    patient = relationship("Patient", back_populates="assessments")


# ── Conversation Session (Interactive Follow-up Loop) ─────────

class ConversationSession(Base):
    """Tracks multi-round follow-up conversations for a single assessment."""
    __tablename__ = "conversation_sessions"

    id = Column(String, primary_key=True, default=_generate_id)
    patient_id = Column(String, ForeignKey("patients.id"), nullable=False, index=True)
    status = Column(String(20), default="active")      # active, completed, abandoned
    current_round = Column(Integer, default=1)
    max_rounds = Column(Integer, default=3)

    # Accumulated diagnostic context
    initial_symptoms = Column(Text, nullable=False)     # original symptom text
    followup_qa = Column(Text, default="[]")            # JSON: [{"question": ..., "answer": ..., "round": N}]
    accumulated_context = Column(Text, default="")      # full context built across rounds

    # Result linkage
    final_assessment_id = Column(String, ForeignKey("assessments.id"), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=_utc_now)
    updated_at = Column(DateTime, default=_utc_now, onupdate=_utc_now)

    # Relationships
    patient = relationship("Patient")
    final_assessment = relationship("Assessment", foreign_keys=[final_assessment_id])
