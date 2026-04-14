# ============================================================
# models/schemas.py — Pydantic Request / Response Schemas
# ============================================================
# Validation schemas for all API endpoints.
# ============================================================

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ══════════════════════════════════════════════════════════════
# AUTH SCHEMAS
# ══════════════════════════════════════════════════════════════

class UserRegister(BaseModel):
    """Registration payload for a new health worker."""
    name: str = Field(..., min_length=2, max_length=100, description="Full name")
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    password: str = Field(..., min_length=6, max_length=128, description="Password (min 6 chars)")
    email: Optional[str] = Field(None, description="Email (optional)")
    phone: Optional[str] = Field(None, max_length=15, description="Phone number")
    village: Optional[str] = Field(None, max_length=100)
    district: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    pincode: Optional[str] = Field(None, max_length=10)
    role: str = Field(default="asha", description="Worker role: asha, anm, doctor, admin")
    preferred_lang: str = Field(default="en", description="ISO 639-1 language code")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Sita Devi",
                "username": "sita_asha",
                "password": "secure123",
                "phone": "9876543210",
                "village": "Ranpur",
                "district": "Nayagarh",
                "state": "Odisha",
                "pincode": "752077",
                "role": "asha",
                "preferred_lang": "or",
            }
        }


class TokenResponse(BaseModel):
    """JWT token response after login/register."""
    access_token: str
    token_type: str = "bearer"
    user_id: str
    name: str


class UserProfile(BaseModel):
    """User profile response."""
    id: str
    name: str
    username: str
    email: Optional[str] = None
    phone: Optional[str] = None
    village: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    role: str
    preferred_lang: str
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str


# ══════════════════════════════════════════════════════════════
# PATIENT SCHEMAS
# ══════════════════════════════════════════════════════════════

class VitalsInput(BaseModel):
    """Vital sign measurements input."""
    temperature_c: Optional[float] = Field(None, ge=30.0, le=45.0, description="Body temperature (°C)")
    bp_systolic: Optional[int] = Field(None, ge=50, le=300, description="Systolic BP (mmHg)")
    bp_diastolic: Optional[int] = Field(None, ge=20, le=200, description="Diastolic BP (mmHg)")
    pulse_bpm: Optional[int] = Field(None, ge=20, le=250, description="Pulse rate (bpm)")
    spo2_pct: Optional[float] = Field(None, ge=0, le=100, description="SpO2 (%)")
    blood_glucose: Optional[float] = Field(None, ge=10, le=800, description="Blood glucose (mg/dL)")
    rr_per_min: Optional[int] = Field(None, ge=5, le=80, description="Respiratory rate (/min)")
    weight_kg: Optional[float] = Field(None, ge=0.5, le=300, description="Weight (kg)")
    notes: Optional[str] = Field(None, max_length=500, description="Additional observations")


class PatientCreate(BaseModel):
    """Create a new patient record."""
    name: str = Field(..., min_length=2, max_length=100)
    age: int = Field(..., ge=0, le=120)
    gender: str = Field(..., description="male, female, or other")
    phone: Optional[str] = Field(None, max_length=15)
    village: Optional[str] = Field(None, max_length=100)
    district: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    known_conditions: Optional[List[str]] = Field(default=[], description="Pre-existing conditions")
    current_medications: Optional[List[str]] = Field(default=[], description="Current medications")
    allergies: Optional[str] = Field(None, max_length=500)
    weight_kg: Optional[float] = Field(None, ge=0.5, le=300)
    height_cm: Optional[float] = Field(None, ge=20, le=250)
    blood_group: Optional[str] = Field(None, max_length=10)
    vitals: Optional[VitalsInput] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Ramesh Kumar",
                "age": 45,
                "gender": "male",
                "phone": "9123456789",
                "village": "Kalinganagar",
                "district": "Jajpur",
                "state": "Odisha",
                "known_conditions": ["diabetes", "hypertension"],
                "current_medications": ["Metformin 500mg", "Amlodipine 5mg"],
                "allergies": "Penicillin",
                "weight_kg": 68.5,
                "height_cm": 165.0,
                "blood_group": "B+",
            }
        }


class PatientOut(BaseModel):
    """Patient response schema."""
    id: str
    name: str
    age: int
    gender: str
    phone: Optional[str] = None
    village: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    known_conditions: List[str] = []
    current_medications: List[str] = []
    allergies: Optional[str] = None
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    blood_group: Optional[str] = None

    class Config:
        from_attributes = True


class PatientUpdate(BaseModel):
    """Partial update for a patient."""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    age: Optional[int] = Field(None, ge=0, le=120)
    gender: Optional[str] = None
    phone: Optional[str] = None
    village: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    known_conditions: Optional[List[str]] = None
    current_medications: Optional[List[str]] = None
    allergies: Optional[str] = None
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    blood_group: Optional[str] = None


# ══════════════════════════════════════════════════════════════
# ASSESSMENT SCHEMAS
# ══════════════════════════════════════════════════════════════

class AssessmentRequest(BaseModel):
    """Text-based health assessment request."""
    patient_id: str = Field(..., description="Patient UUID")
    symptoms: str = Field(..., min_length=5, max_length=2000, description="Described symptoms")
    language: str = Field(default="en", description="ISO 639-1 language code")
    vitals: Optional[VitalsInput] = None

    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": "abc-123-def",
                "symptoms": "Patient has high fever for 3 days with chills, body pain, headache. "
                            "No rash. Lives near rice fields. Post-monsoon season.",
                "language": "en",
                "vitals": {
                    "temperature_c": 39.5,
                    "bp_systolic": 110,
                    "bp_diastolic": 70,
                    "pulse_bpm": 96,
                    "spo2_pct": 97.0,
                },
            }
        }


class AssessmentResponse(BaseModel):
    """Full assessment result with optional follow-up loop data."""
    model_config = {"from_attributes": True, "protected_namespaces": ()}

    id: str
    patient_id: str
    input_type: str
    symptoms_text: str
    risk_level: str
    risk_reason: str
    possible_conditions: list
    next_steps: list
    patient_summary: str
    model_used: Optional[str] = None
    confidence: float
    created_at: str

    # Interactive follow-up fields
    needs_followup: bool = False
    followup_questions: List[str] = []
    session_id: Optional[str] = None
    round_number: int = 1


# ══════════════════════════════════════════════════════════════
# FOLLOW-UP / INTERACTIVE LOOP SCHEMAS
# ══════════════════════════════════════════════════════════════

class FollowupRequest(BaseModel):
    """Submit answers to follow-up questions in an active session."""
    session_id: str = Field(..., description="Active conversation session ID")
    answers: dict = Field(..., description="Map of question→answer, e.g. {'duration': '3 days'}")
    language: str = Field(default="en", description="ISO 639-1 language code")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "sess-abc-123",
                "answers": {
                    "How long has the fever lasted?": "3 days",
                    "Is there any rash?": "Yes, on the arms",
                },
                "language": "en",
            }
        }


# ══════════════════════════════════════════════════════════════
# rPPG VITAL SIGNS SCHEMAS
# ══════════════════════════════════════════════════════════════

class RPPGVitalsResult(BaseModel):
    """Camera-based vital sign extraction result."""
    heart_rate_bpm: Optional[float] = Field(None, description="Estimated heart rate (bpm)")
    respiratory_rate_per_min: Optional[float] = Field(None, description="Estimated respiratory rate (/min)")
    spo2_estimate_pct: Optional[float] = Field(None, description="Estimated SpO2 (%)")
    signal_quality: str = Field(default="unknown", description="Signal quality: good, moderate, low")
    method: str = Field(default="rPPG (camera-based, non-invasive)", description="Measurement method")
    duration_seconds: Optional[float] = Field(None, description="Duration of video analysed")


class ChangePasswordRequest(BaseModel):
    """Change password request body."""
    old_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=6, max_length=128)
