# ============================================================
# routers/assessment.py — Health Assessment Endpoints
# ============================================================
# Input modes:
#   POST /assessment/text      — typed symptoms + optional vitals
#   POST /assessment/voice     — audio file upload
#   POST /assessment/image     — image file + optional text
#   POST /assessment/followup  — submit follow-up answers (interactive loop)
#   POST /assessment/rppg-vitals — camera-based vital sign extraction
#   GET  /assessment/session/{id} — get conversation session state
#
# All assessment modes go through the RAG → MedGemma pipeline.
# Interactive loop: if LLM confidence < threshold, it asks
# follow-up questions (max 3 rounds) before final assessment.
# ============================================================

import json
import uuid
from pathlib import Path
from typing import Optional

from fastapi import (
    APIRouter, Depends, HTTPException, UploadFile, File, Form
)
from loguru import logger
from sqlalchemy.orm import Session

from config import settings
from database.sqlite_db import get_db
from models.db_models import (
    Assessment, Patient, ConversationSession, InputType, RiskLevel
)
from models.schemas import AssessmentRequest, FollowupRequest
from services.rag_service import rag_service
from services.llm_service import llm_service
from services.voice_service import voice_service
from services.image_service import image_service

router = APIRouter(prefix="/assessment", tags=["Assessment"])

ALLOWED_IMAGE_TYPES = {
    "image/jpeg", "image/jpg", "image/png", "image/webp", "image/bmp"
}
ALLOWED_AUDIO_TYPES = {
    "audio/wav", "audio/mpeg", "audio/mp4", "audio/ogg",
    "audio/x-wav", "audio/webm", "audio/m4a",
}
ALLOWED_VIDEO_TYPES = {
    "video/mp4", "video/webm", "video/avi", "video/x-msvideo",
    "video/quicktime",
}


# ── Core RAG-Assessment pipeline ──────────────────────────────

def _run_assessment(
    patient_id: str,
    symptoms_text: str,
    input_type: InputType,
    db: Session,
    image_path: Optional[str] = None,
    voice_path: Optional[str] = None,
    vitals_dict: Optional[dict] = None,
    language: str = "en",
    session_id: Optional[str] = None,
    accumulated_context: Optional[str] = None,
) -> dict:
    """
    Central assessment function shared by all input modes.
    1. Validate patient exists
    2. RAG: retrieve relevant disease knowledge
    3. Build prompt
    4. LLM inference via MedGemma GGUF
    5. Parse and store result
    6. Handle interactive follow-up loop
    """
    # 1. Fetch patient
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(404, detail="Patient not found.")

    patient_dict = {
        "name": patient.name,
        "age": patient.age,
        "gender": patient.gender.value if hasattr(patient.gender, "value") else patient.gender,
        "village": patient.village,
        "district": patient.district,
        "state": patient.state,
        "known_conditions": json.loads(patient.known_conditions) if patient.known_conditions else [],
        "current_medications": json.loads(patient.current_medications) if patient.current_medications else [],
        "allergies": patient.allergies,
        "weight_kg": patient.weight_kg,
        "height_cm": patient.height_cm,
    }

    # 2. RAG retrieval — find relevant disease knowledge
    query_text = symptoms_text
    if accumulated_context:
        query_text = f"{accumulated_context}\n\n{symptoms_text}"
    retrieved_chunks = rag_service.retrieve_disease_context(query_text)

    # 3. Build prompt
    prompt = rag_service.build_assessment_prompt(
        symptoms=query_text,
        patient_info=patient_dict,
        retrieved_chunks=retrieved_chunks,
        vitals=vitals_dict,
        language=language,
    )

    # 4. LLM inference via MedGemma
    try:
        raw_response = llm_service.generate(
            prompt=prompt,
            temperature=settings.MEDGEMMA_TEMPERATURE,
        )
    except Exception as e:
        raise HTTPException(503, detail=f"LLM unavailable: {str(e)}")

    # 5. Parse LLM JSON response
    try:
        result = llm_service.parse_json_response(raw_response)
    except (ValueError, json.JSONDecodeError) as e:
        raise HTTPException(500, detail=f"Failed to parse LLM response: {str(e)}")

    # Extract follow-up information
    needs_followup = result.get("needs_followup", False)
    followup_questions = result.get("followup_questions", [])
    confidence = float(result.get("confidence", 0.5))

    # Validate and normalise risk level
    risk_raw = result.get("risk_level", "NORMAL").upper()
    if risk_raw not in ("EMERGENCY", "URGENT", "NORMAL"):
        risk_raw = "NORMAL"

    # 6. Handle conversation session for interactive loop
    session = None
    round_number = 1

    if session_id:
        # Existing session — update it
        session = db.query(ConversationSession).filter(
            ConversationSession.id == session_id
        ).first()
        if session:
            round_number = session.current_round

    if needs_followup and followup_questions and round_number < settings.MAX_FOLLOWUP_ROUNDS:
        # Create or update session for follow-up
        if not session:
            session = ConversationSession(
                patient_id=patient_id,
                initial_symptoms=symptoms_text,
                accumulated_context=query_text,
                current_round=1,
                max_rounds=settings.MAX_FOLLOWUP_ROUNDS,
            )
            db.add(session)
            db.commit()
            db.refresh(session)

        # Return follow-up response without saving assessment yet
        return {
            "id": None,
            "patient_id": patient_id,
            "input_type": input_type.value if hasattr(input_type, "value") else input_type,
            "symptoms_text": symptoms_text,
            "risk_level": risk_raw,
            "risk_reason": result.get("risk_reason", ""),
            "possible_conditions": result.get("possible_conditions", []),
            "next_steps": result.get("next_steps", []),
            "patient_summary": result.get("patient_summary", ""),
            "model_used": llm_service.get_model_name(),
            "confidence": confidence,
            "created_at": None,
            "needs_followup": True,
            "followup_questions": followup_questions,
            "session_id": session.id,
            "round_number": round_number,
        }

    # 7. Save final assessment to SQLite
    assessment = Assessment(
        patient_id=patient_id,
        input_type=input_type,
        symptoms_text=symptoms_text if not accumulated_context else accumulated_context,
        image_path=image_path,
        voice_path=voice_path,
        possible_conditions=json.dumps(result.get("possible_conditions", [])),
        risk_level=RiskLevel(risk_raw),
        risk_reason=result.get("risk_reason", ""),
        next_steps=json.dumps(result.get("next_steps", [])),
        patient_summary=result.get("patient_summary", ""),
        retrieved_chunks=json.dumps([
            {"name": c["metadata"].get("name"), "similarity": c["similarity"]}
            for c in retrieved_chunks
        ]),
        model_used=llm_service.get_model_name(),
        confidence=confidence,
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)

    # Mark session as completed if exists
    if session:
        session.status = "completed"
        session.final_assessment_id = assessment.id
        db.commit()

    response = _format_response(assessment)
    response["needs_followup"] = False
    response["followup_questions"] = []
    response["session_id"] = session.id if session else None
    response["round_number"] = round_number
    return response


def _run_assessment_safe(**kwargs) -> dict:
    """Wrap assessment execution so unexpected exceptions still return JSON errors."""
    try:
        return _run_assessment(**kwargs)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Assessment pipeline failed for patient={kwargs.get('patient_id')}")
        raise HTTPException(500, detail=f"Assessment pipeline failed: {str(e)}")


def _format_response(a: Assessment) -> dict:
    return {
        "id": a.id,
        "patient_id": a.patient_id,
        "input_type": a.input_type.value if hasattr(a.input_type, "value") else a.input_type,
        "symptoms_text": a.symptoms_text,
        "risk_level": a.risk_level.value if hasattr(a.risk_level, "value") else a.risk_level,
        "risk_reason": a.risk_reason,
        "possible_conditions": json.loads(a.possible_conditions) if a.possible_conditions else [],
        "next_steps": json.loads(a.next_steps) if a.next_steps else [],
        "patient_summary": a.patient_summary,
        "model_used": a.model_used,
        "confidence": a.confidence,
        "created_at": a.created_at.isoformat() if a.created_at else None,
    }


# ── Endpoint 1: Text Input ─────────────────────────────────────

@router.post("/text", summary="Assess using typed symptoms")
def assess_text(
    payload: AssessmentRequest,
    db: Session = Depends(get_db),
):
    """
    Submit typed symptoms and optional vitals for AI health assessment.
    Most common input for literate health workers.
    If the AI needs more information, it will return follow-up questions.
    """
    vitals = payload.vitals.model_dump(exclude_none=True) if payload.vitals else None
    return _run_assessment_safe(
        patient_id=payload.patient_id,
        symptoms_text=payload.symptoms,
        input_type=InputType.TEXT,
        db=db,
        vitals_dict=vitals,
        language=payload.language,
    )


# ── Endpoint 2: Voice Input ────────────────────────────────────

@router.post("/voice", summary="Assess using voice recording")
async def assess_voice(
    patient_id: str = Form(...),
    language: str = Form(default="hi"),
    audio_file: UploadFile = File(..., description="Audio file (wav/mp3/ogg/m4a)"),
    temperature: Optional[float] = Form(default=None),
    bp_systolic: Optional[int] = Form(default=None),
    bp_diastolic: Optional[int] = Form(default=None),
    pulse_bpm: Optional[int] = Form(default=None),
    spo2_pct: Optional[float] = Form(default=None),
    db: Session = Depends(get_db),
):
    """
    Upload a voice recording (in any Indian language) for assessment.
    Online: transcribed via Sarvam AI Saaras v2 API.
    Offline: transcribed via AI4Bharat IndicConformer (22 Indian languages).
    Ideal for ASHA workers with low literacy.
    """
    if audio_file.content_type not in ALLOWED_AUDIO_TYPES:
        raise HTTPException(
            415,
            detail=f"Unsupported audio type: {audio_file.content_type}. "
                   f"Supported: {ALLOWED_AUDIO_TYPES}"
        )

    # Save audio file
    filename = f"{uuid.uuid4()}{Path(audio_file.filename).suffix or '.wav'}"
    audio_path = settings.UPLOADS_DIR / filename
    content = await audio_file.read()
    with open(audio_path, "wb") as f:
        f.write(content)

    # Transcribe (Sarvam API → IndicConformer fallback)
    try:
        transcribed_text, detected_lang = voice_service.transcribe(
            str(audio_path), language=language
        )
    except Exception as e:
        raise HTTPException(500, detail=f"Voice transcription failed: {str(e)}")

    if not transcribed_text.strip():
        raise HTTPException(422, detail="Could not transcribe audio — no speech detected.")

    # Build vitals dict from form fields
    vitals = {}
    if temperature: vitals["temperature_c"] = temperature
    if bp_systolic:  vitals["bp_systolic"]  = bp_systolic
    if bp_diastolic: vitals["bp_diastolic"] = bp_diastolic
    if pulse_bpm:    vitals["pulse_bpm"]    = pulse_bpm
    if spo2_pct:     vitals["spo2_pct"]     = spo2_pct

    result = _run_assessment_safe(
        patient_id=patient_id,
        symptoms_text=transcribed_text,
        input_type=InputType.VOICE,
        db=db,
        voice_path=str(audio_path),
        vitals_dict=vitals or None,
        language=detected_lang or language,
    )
    result["transcribed_text"] = transcribed_text
    result["detected_language"] = detected_lang
    return result


# ── Endpoint 3: Image Input ────────────────────────────────────

@router.post("/image", summary="Assess using image (skin/wound/report)")
async def assess_image(
    patient_id: str = Form(...),
    language: str = Form(default="en"),
    additional_symptoms: Optional[str] = Form(default=None),
    image_file: UploadFile = File(..., description="Image (jpg/png/webp)"),
    db: Session = Depends(get_db),
):
    """
    Upload a photo for AI assessment.
    Supported: skin rashes, wounds, infections, lab reports.
    EfficientNetV2-Small classifies the image and generates a text
    description, which is then processed by the RAG → MedGemma pipeline.
    """
    if image_file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            415,
            detail=f"Unsupported image type: {image_file.content_type}. "
                   f"Supported: {ALLOWED_IMAGE_TYPES}"
        )

    # Save image file
    filename = f"{uuid.uuid4()}{Path(image_file.filename).suffix or '.jpg'}"
    img_path = settings.UPLOADS_DIR / filename
    content = await image_file.read()
    with open(img_path, "wb") as f:
        f.write(content)

    # Get image description from EfficientNetV2
    try:
        image_description = image_service.describe_image(str(img_path))
    except Exception as e:
        raise HTTPException(500, detail=f"Image analysis failed: {str(e)}")

    # Combine image description with any additional text symptoms
    combined_symptoms = image_description
    if additional_symptoms:
        combined_symptoms = f"{additional_symptoms}\n\nImage description: {image_description}"

    input_type = InputType.MIXED if additional_symptoms else InputType.IMAGE

    result = _run_assessment_safe(
        patient_id=patient_id,
        symptoms_text=combined_symptoms,
        input_type=input_type,
        db=db,
        image_path=str(img_path),
        language=language,
    )
    result["image_description"] = image_description
    return result


# ── Endpoint 4: Follow-up (Interactive Loop) ──────────────────

@router.post("/followup", summary="Submit follow-up answers")
def assess_followup(
    payload: FollowupRequest,
    db: Session = Depends(get_db),
):
    """
    Submit answers to follow-up questions from a previous assessment.
    The system accumulates context across rounds (max 3) to build
    a more accurate diagnosis — mimicking how a real doctor would
    ask clarifying questions before concluding.
    """
    # Fetch the active conversation session
    session = db.query(ConversationSession).filter(
        ConversationSession.id == payload.session_id,
        ConversationSession.status == "active",
    ).first()

    if not session:
        raise HTTPException(404, detail="Session not found or already completed.")

    # Increment round
    session.current_round += 1

    # Append Q&A to history
    qa_history = json.loads(session.followup_qa or "[]")
    for question, answer in payload.answers.items():
        qa_history.append({
            "question": question,
            "answer": answer,
            "round": session.current_round,
        })
    session.followup_qa = json.dumps(qa_history)

    # Build accumulated context from all rounds
    context_parts = [session.initial_symptoms]
    for qa in qa_history:
        context_parts.append(f"Q: {qa['question']}")
        context_parts.append(f"A: {qa['answer']}")

    accumulated = "\n".join(context_parts)
    session.accumulated_context = accumulated

    db.commit()

    # Run assessment again with all accumulated context
    return _run_assessment_safe(
        patient_id=session.patient_id,
        symptoms_text=accumulated,
        input_type=InputType.TEXT,
        db=db,
        language=payload.language,
        session_id=session.id,
        accumulated_context=accumulated,
    )


# ── Endpoint 5: rPPG Vital Signs ──────────────────────────────

@router.post("/rppg-vitals", summary="Extract vitals from facial video")
async def extract_rppg_vitals(
    patient_id: str = Form(...),
    video_file: UploadFile = File(..., description="Short facial video (10-15s, mp4/webm)"),
    db: Session = Depends(get_db),
):
    """
    Upload a short video of the patient's face (10-15 seconds) to extract
    vital signs using remote photoplethysmography (rPPG).

    Extracts:
    - Heart Rate (HR) from skin colour changes
    - Respiratory Rate (RR) from breathing modulation
    - SpO2 estimate from red/blue channel ratio

    No hardware sensors needed — works with any smartphone camera.
    Based on: ArXiv 2508.18787v1 (Face2PPG pipeline).
    """
    from services.rppg_service import rppg_service

    if not settings.RPPG_ENABLED:
        raise HTTPException(503, detail="rPPG service is disabled in configuration.")

    if video_file.content_type not in ALLOWED_VIDEO_TYPES:
        raise HTTPException(
            415,
            detail=f"Unsupported video type: {video_file.content_type}. "
                   f"Supported: {ALLOWED_VIDEO_TYPES}"
        )

    # Verify patient exists
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(404, detail="Patient not found.")

    # Save video file
    filename = f"{uuid.uuid4()}{Path(video_file.filename).suffix or '.mp4'}"
    video_path = settings.UPLOADS_DIR / filename
    content = await video_file.read()
    with open(video_path, "wb") as f:
        f.write(content)

    # Extract vitals
    try:
        vitals = rppg_service.extract_vitals_from_video(str(video_path))
    except Exception as e:
        raise HTTPException(500, detail=f"rPPG extraction failed: {str(e)}")

    vitals["patient_id"] = patient_id
    return vitals


# ── Endpoint 6: Get Conversation Session ──────────────────────

@router.get("/session/{session_id}", summary="Get conversation session state")
def get_session(
    session_id: str,
    db: Session = Depends(get_db),
):
    """Retrieve the full state of an interactive conversation session."""
    session = db.query(ConversationSession).filter(
        ConversationSession.id == session_id
    ).first()
    if not session:
        raise HTTPException(404, detail="Session not found.")

    return {
        "id": session.id,
        "patient_id": session.patient_id,
        "status": session.status,
        "current_round": session.current_round,
        "max_rounds": session.max_rounds,
        "initial_symptoms": session.initial_symptoms,
        "followup_qa": json.loads(session.followup_qa or "[]"),
        "accumulated_context": session.accumulated_context,
        "final_assessment_id": session.final_assessment_id,
        "created_at": session.created_at.isoformat() if session.created_at else None,
        "updated_at": session.updated_at.isoformat() if session.updated_at else None,
    }


# ── Assessment History ─────────────────────────────────────────

@router.get("/patient/{patient_id}", summary="Get assessment history for a patient")
def get_patient_assessments(
    patient_id: str,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    """Retrieve all past assessments for a patient."""
    assessments = (
        db.query(Assessment)
        .filter(Assessment.patient_id == patient_id)
        .order_by(Assessment.created_at.desc())
        .limit(limit)
        .all()
    )
    return [_format_response(a) for a in assessments]


@router.get("/{assessment_id}", summary="Get a single assessment")
def get_assessment(
    assessment_id: str,
    db: Session = Depends(get_db),
):
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(404, detail="Assessment not found.")
    return _format_response(assessment)
