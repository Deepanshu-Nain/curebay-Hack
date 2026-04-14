# ============================================================
# services/rag_service.py — RAG Pipeline
# ============================================================
# Retrieval-Augmented Generation (RAG) for CureBay.
# 
# Pipeline:
#   1. Embed query using MiniLM (all-MiniLM-L6-v2)
#   2. Retrieve top-K similar chunks from ChromaDB  
#   3. Build context-aware prompt from retrieved chunks + 
#      patient profile
#   4. Generate response with MedGemma GGUF via llama-cpp-python
# ============================================================

import json
from typing import List, Dict, Any, Optional, Tuple
from loguru import logger

from config import settings
from database.vector_db import vector_db
from services.embedding_service import embedding_service


class RAGService:

    def __init__(self):
        self._disease_collection = settings.VECTOR_COLLECTION_DISEASE
        self._patient_collection = settings.VECTOR_COLLECTION_PATIENTS
        self._top_k = settings.RAG_TOP_K
        self._threshold = settings.RAG_SIMILARITY_THRESHOLD

    # ── Knowledge Base Seeding ─────────────────────────────────

    def seed_disease_knowledge(self, force: bool = False) -> int:
        """
        Seed the vector DB with disease knowledge base documents.
        Skips if already seeded unless force=True.
        Returns the number of documents indexed.
        """
        from data.diseases_kb import get_all_documents

        if not force and vector_db.collection_exists_and_populated(self._disease_collection):
            count = vector_db.count(self._disease_collection)
            logger.info(f"Disease KB already seeded ({count} docs). Skipping.")
            return count

        logger.info("Seeding disease knowledge base into vector DB...")
        docs = get_all_documents()

        ids, texts, metadatas = zip(*docs)
        logger.info(f"Generating embeddings for {len(texts)} disease documents...")
        embeddings = embedding_service.embed_batch([t for t in texts])

        vector_db.upsert(
            collection_name=self._disease_collection,
            ids=list(ids),
            embeddings=embeddings,
            documents=list(texts),
            metadatas=list(metadatas),
        )
        logger.success(f"Disease KB seeded: {len(docs)} documents.")
        return len(docs)

    # ── Patient Context Indexing ───────────────────────────────

    def index_patient(self, patient_id: str, patient_data: Dict[str, Any]) -> None:
        """
        Index a patient's profile and medical history into the patient 
        context collection so the LLM can personalise responses.
        """
        text = self._build_patient_text(patient_data)
        embedding = embedding_service.embed_document(text)
        vector_db.upsert(
            collection_name=self._patient_collection,
            ids=[patient_id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[{
                "patient_id": patient_id,
                "name": patient_data.get("name", ""),
                "age": str(patient_data.get("age", "")),
                "gender": patient_data.get("gender", ""),
            }],
        )
        logger.debug(f"Indexed patient context: {patient_id}")

    def delete_patient_context(self, patient_id: str) -> None:
        vector_db.delete(self._patient_collection, [patient_id])

    # ── Retrieval ──────────────────────────────────────────────

    def retrieve_disease_context(
        self,
        query: str,
        top_k: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Given a symptom query, retrieve the most semantically relevant 
        disease knowledge chunks from the vector store.
        """
        k = top_k or self._top_k
        query_emb = embedding_service.embed_query(query)

        results = vector_db.query(
            collection_name=self._disease_collection,
            query_embeddings=[query_emb],
            n_results=k,
        )

        chunks = []
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for doc, meta, dist in zip(documents, metadatas, distances):
            # ChromaDB cosine returns distance (0 = identical, 2 = opposite)
            # Convert to similarity score: 1 - (distance/2)
            similarity = 1.0 - (dist / 2.0)
            if similarity >= self._threshold:
                chunks.append({
                    "text": doc,
                    "metadata": meta,
                    "similarity": round(similarity, 4),
                })

        logger.debug(f"Retrieved {len(chunks)} disease chunks for query.")
        return chunks

    def retrieve_patient_context(self, patient_id: str) -> Optional[str]:
        """Retrieve the indexed patient profile text."""
        try:
            results = vector_db.query(
                collection_name=self._patient_collection,
                query_embeddings=[embedding_service.embed_query(patient_id)],
                n_results=1,
                where={"patient_id": patient_id},
            )
            docs = results.get("documents", [[]])[0]
            return docs[0] if docs else None
        except Exception as e:
            logger.warning(f"Patient context retrieval failed: {e}")
            return None

    # ── Prompt Builder ─────────────────────────────────────────

    def build_assessment_prompt(
        self,
        symptoms: str,
        patient_info: Dict[str, Any],
        retrieved_chunks: List[Dict[str, Any]],
        vitals: Optional[Dict[str, Any]] = None,
        language: str = "en",
    ) -> str:
        """
        Construct the full RAG-augmented prompt for health assessment.
        """
        # Format retrieved disease knowledge
        knowledge_section = ""
        if retrieved_chunks:
            knowledge_section = "\n\n## Relevant Medical Knowledge (Retrieved):\n"
            for i, chunk in enumerate(retrieved_chunks[:4], 1):
                meta = chunk.get("metadata", {})
                sim = chunk.get("similarity", 0)
                knowledge_section += (
                    f"\n### [{i}] {meta.get('name', 'Unknown')} "
                    f"(relevance: {sim:.0%})\n"
                    f"{chunk['text'][:800]}\n"
                )

        # Format patient profile
        patient_section = self._format_patient_for_prompt(patient_info)

        # Format vitals
        vitals_section = ""
        if vitals:
            vitals_section = "\n## Current Vitals:\n"
            vmap = {
                "temperature_c": ("Temperature", "°C"),
                "bp_systolic": ("BP Systolic", "mmHg"),
                "bp_diastolic": ("BP Diastolic", "mmHg"),
                "pulse_bpm": ("Pulse", "bpm"),
                "spo2_pct": ("SpO2", "%"),
                "blood_glucose": ("Blood Glucose", "mg/dL"),
                "rr_per_min": ("Respiratory Rate", "/min"),
            }
            for key, (label, unit) in vmap.items():
                val = vitals.get(key)
                if val is not None:
                    vitals_section += f"- {label}: {val} {unit}\n"

        lang_instruction = ""
        if language != "en":
            lang_instruction = (
                f"\nNote: The health worker may be working in a non-English environment. "
                f"Provide the patient_summary field in both English and simple terms suitable "
                f"for a non-expert health worker.\n"
            )

        prompt = f"""You are CureBay AI, a medical decision-support assistant for rural 
ASHA workers and frontline health workers in India. You help with preliminary health 
assessment — you do NOT replace a doctor but help workers triage and take appropriate action.

{patient_section}{vitals_section}

## Reported Symptoms:
{symptoms}
{knowledge_section}{lang_instruction}

## Instructions:
Based on the patient information, reported symptoms, vitals (if provided), and the 
retrieved medical knowledge above, provide a structured health assessment.

You MUST respond with ONLY a valid JSON object (no other text) in this exact format:
{{
  "possible_conditions": [
    {{
      "name": "Disease name",
      "probability": "High|Medium|Low",
      "description": "Brief explanation of why this matches the symptoms"
    }}
  ],
  "risk_level": "EMERGENCY|URGENT|NORMAL",
  "risk_reason": "Clear explanation of the risk level and what is driving it",
  "next_steps": [
    "Specific action 1",
    "Specific action 2",
    "Specific action 3"
  ],
  "patient_summary": "Structured 3–5 sentence summary suitable for referral letter or record: patient details, chief complaint, key findings, preliminary assessment, and recommended action.",
  "confidence": 0.0
}}

Rules:
- List 2–3 most likely conditions only.
- EMERGENCY = immediate life threat requiring referral NOW.
- URGENT = needs medical consultation within hours/same day.
- NORMAL = can be managed with basic care and monitoring.
- next_steps must be specific, actionable steps for an ASHA worker.
- confidence is a float 0.0–1.0 reflecting how certain you are given available information.
- Prioritise patient safety — when in doubt, recommend referral.
- If you do NOT have enough information to make a confident assessment (confidence < 0.6),
  you MUST set "needs_followup" to true and provide 2–3 specific follow-up questions in
  "followup_questions" array. Example followup_questions:
  - "How many days has the fever lasted?"
  - "Is there any blood in the stool?" 
  - "Has the patient traveled recently?"
- If you have enough information, set "needs_followup" to false and leave "followup_questions" as empty array.

Your response MUST also include these additional fields in the JSON:
  "needs_followup": true/false,
  "followup_questions": ["question1", "question2", ...]
"""
        return prompt

    # ── Helpers ────────────────────────────────────────────────

    def _build_patient_text(self, p: Dict[str, Any]) -> str:
        lines = [
            f"Patient: {p.get('name', 'Unknown')}",
            f"Age: {p.get('age', '?')} years",
            f"Gender: {p.get('gender', '?')}",
            f"Location: {p.get('village', '')}, {p.get('district', '')}, {p.get('state', '')}",
        ]
        if p.get("known_conditions"):
            conditions = p["known_conditions"]
            if isinstance(conditions, str):
                conditions = json.loads(conditions)
            lines.append(f"Known conditions: {', '.join(conditions)}")
        if p.get("current_medications"):
            meds = p["current_medications"]
            if isinstance(meds, str):
                meds = json.loads(meds)
            lines.append(f"Current medications: {', '.join(meds)}")
        if p.get("allergies"):
            lines.append(f"Allergies: {p['allergies']}")
        if p.get("weight_kg"):
            lines.append(f"Weight: {p['weight_kg']} kg")
        if p.get("height_cm"):
            lines.append(f"Height: {p['height_cm']} cm")
        return "\n".join(lines)

    def _format_patient_for_prompt(self, p: Dict[str, Any]) -> str:
        text = self._build_patient_text(p)
        return f"## Patient Profile:\n{text}\n"


# Singleton
rag_service = RAGService()
