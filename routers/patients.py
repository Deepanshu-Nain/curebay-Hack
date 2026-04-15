# ============================================================
# routers/patients.py — Patient Record Management
# ============================================================

import json
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database.sqlite_db import get_db
from models.db_models import Patient, VitalRecord
from models.schemas import PatientCreate, PatientOut, PatientUpdate, VitalsInput, MessageResponse
from services.rag_service import rag_service

router = APIRouter(prefix="/patients", tags=["Patients"])


# ── Helper ────────────────────────────────────────────────────

def _patient_to_dict(p: Patient) -> dict:
    return {
        "id": p.id,
        "name": p.name,
        "age": p.age,
        "gender": p.gender.value if hasattr(p.gender, "value") else p.gender,
        "phone": p.phone,
        "village": p.village,
        "district": p.district,
        "state": p.state,
        "known_conditions": json.loads(p.known_conditions) if p.known_conditions else [],
        "current_medications": json.loads(p.current_medications) if p.current_medications else [],
        "allergies": p.allergies,
        "weight_kg": p.weight_kg,
        "height_cm": p.height_cm,
        "blood_group": p.blood_group,
    }


# ── Endpoints ─────────────────────────────────────────────────

@router.post("/", status_code=201)
def create_patient(
    payload: PatientCreate,
    db: Session = Depends(get_db),
):
    """Register a new patient."""
    patient = Patient(
        name=payload.name,
        age=payload.age,
        gender=payload.gender,
        phone=payload.phone,
        village=payload.village,
        district=payload.district,
        state=payload.state,
        known_conditions=json.dumps(payload.known_conditions or []),
        current_medications=json.dumps(payload.current_medications or []),
        allergies=payload.allergies,
        weight_kg=payload.weight_kg,
        height_cm=payload.height_cm,
        blood_group=payload.blood_group,
        registered_by_id=None,
    )
    db.add(patient)

    # Add vitals if provided
    if payload.vitals:
        db.flush()  # ensure patient.id is available
        vitals = VitalRecord(
            patient_id=patient.id,
            **payload.vitals.model_dump(exclude_none=True),
        )
        db.add(vitals)

    db.commit()
    db.refresh(patient)

    # Index patient context in vector DB for personalised RAG
    try:
        rag_service.index_patient(patient.id, _patient_to_dict(patient))
    except Exception:
        # Non-fatal — assessment will still work without personalised context
        pass

    return _patient_to_dict(patient)


@router.get("/")
def list_patients(
    search: Optional[str] = Query(None, description="Search by name, phone, or village"),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """List all patients."""
    query = db.query(Patient)

    if search:
        like = f"%{search}%"
        query = query.filter(
            (Patient.name.ilike(like)) |
            (Patient.phone.ilike(like)) |
            (Patient.village.ilike(like))
        )

    patients = query.order_by(Patient.created_at.desc()).offset(skip).limit(limit).all()
    return [_patient_to_dict(p) for p in patients]


@router.get("/{patient_id}")
def get_patient(
    patient_id: str,
    db: Session = Depends(get_db),
):
    """Get a patient's full profile."""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(404, detail="Patient not found.")
    return _patient_to_dict(patient)


@router.put("/{patient_id}")
def update_patient(
    patient_id: str,
    payload: PatientUpdate,
    db: Session = Depends(get_db),
):
    """Update a patient's profile."""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(404, detail="Patient not found.")

    update_data = payload.model_dump(exclude_none=True)
    for field, value in update_data.items():
        if field in ("known_conditions", "current_medications") and isinstance(value, list):
            setattr(patient, field, json.dumps(value))
        else:
            setattr(patient, field, value)

    db.commit()
    db.refresh(patient)

    # Re-index updated patient context
    try:
        rag_service.index_patient(patient.id, _patient_to_dict(patient))
    except Exception:
        pass

    return _patient_to_dict(patient)


@router.delete("/{patient_id}", response_model=MessageResponse)
def delete_patient(
    patient_id: str,
    db: Session = Depends(get_db),
):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(404, detail="Patient not found.")
    db.delete(patient)
    db.commit()
    try:
        rag_service.delete_patient_context(patient_id)
    except Exception:
        pass
    return MessageResponse(message="Patient deleted.")


# ── Vitals ────────────────────────────────────────────────────

@router.post("/{patient_id}/vitals", status_code=201)
def add_vitals(
    patient_id: str,
    vitals: VitalsInput,
    db: Session = Depends(get_db),
):
    """Record a new set of vitals for a patient."""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(404, detail="Patient not found.")

    record = VitalRecord(
        patient_id=patient_id,
        **vitals.model_dump(exclude_none=True),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return {"id": record.id, "recorded_at": record.recorded_at}


@router.get("/{patient_id}/vitals")
def get_vitals_history(
    patient_id: str,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    """Get vital sign history for a patient."""
    records = (
        db.query(VitalRecord)
        .filter(VitalRecord.patient_id == patient_id)
        .order_by(VitalRecord.recorded_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": r.id,
            "temperature_c": r.temperature_c,
            "bp_systolic": r.bp_systolic,
            "bp_diastolic": r.bp_diastolic,
            "pulse_bpm": r.pulse_bpm,
            "spo2_pct": r.spo2_pct,
            "blood_glucose": r.blood_glucose,
            "rr_per_min": r.rr_per_min,
            "notes": r.notes,
            "recorded_at": r.recorded_at,
        }
        for r in records
    ]
