# CureBay AI Health Assistant — Architecture

## Overview
Fully offline, multimodal health assessment system for rural ASHA workers.
Runs on low-resource Android tablets — **no cloud, no Ollama, no internet required**.

## Architecture (v2.0 — Offline-First)

```
┌───────────────────────────────────────────────────────────┐
│                    FastAPI Application                     │
│                  (uvicorn, port 8000)                      │
├───────────┬───────────┬──────────┬──────────┬─────────────┤
│  /text    │  /voice   │  /image  │ /followup│ /rppg-vitals│
│  endpoint │  endpoint │  endpoint│ endpoint │  endpoint   │
└─────┬─────┴─────┬─────┴────┬─────┴────┬─────┴──────┬──────┘
      │           │          │          │             │
      │     ┌─────▼──────┐  │          │      ┌──────▼──────┐
      │     │ Sarvam AI  │  │          │      │ rPPG Service│
      │     │ (online) / │  │          │      │ face→vitals │
      │     │ AI4Bharat  │  │          │      │ HR/RR/SpO2  │
      │     │IndicConf.  │  │          │      └─────────────┘
      │     │ (offline)  │  │          │
      │     └─────┬──────┘  │          │
      │           │    ┌────▼────┐     │
      │           │    │EfficNet │     │
      │           │    │V2-Small │     │
      │           │    │(20 MB)  │     │
      │           │    └────┬────┘     │
      │           │         │          │
      ▼           ▼         ▼          │
┌─────────────────────────────────┐    │
│     Unified Text Layer          │    │
│   (symptoms + descriptions)     │    │
└──────────────┬──────────────────┘    │
               │                       │
       ┌───────▼──────────┐            │
       │ MiniLM Embeddings│            │
       │ (80 MB, 384-dim) │            │
       └───────┬──────────┘            │
               │                       │
       ┌───────▼──────────┐            │
       │    ChromaDB       │           │
       │  Disease KB       │           │
       └───────┬──────────┘            │
               │ top-K contexts        │
       ┌───────▼──────────┐            │
       │  Prompt Builder   │◄──────────┘
       │  (RAG pipeline)   │ (accumulated follow-up context)
       └───────┬──────────┘
               │
       ┌───────▼──────────────┐
       │  MedGemma Q4_K_M     │
       │  (2.7 GB, llama.cpp) │
       └───────┬──────────────┘
               │
       ┌───────▼──────────┐
       │ Response Handler  │
       │ ├─ confidence≥0.6 → Final Assessment → SQLite
       │ └─ confidence<0.6 → Follow-up Questions (max 3 rounds)
       └──────────────────┘
```

## Model Stack

| Component | Model | Size | Framework |
|-----------|-------|------|-----------|
| LLM | MedGemma-1.5-4b-it Q4_K_M | ~2.7 GB | llama-cpp-python |
| Text Embeddings | all-MiniLM-L6-v2 | ~80 MB | sentence-transformers |
| Offline STT | AI4Bharat IndicConformer | ~600 MB | NVIDIA NeMo |
| Online STT | Sarvam AI Saaras v2 | API | requests |
| Image Classification | EfficientNetV2-Small | ~20 MB | torchvision |
| rPPG Vitals | Face2PPG pipeline | ~2 MB | OpenCV + scipy |
| Vector Store | ChromaDB | varies | chromadb |
| Database | SQLite | varies | sqlalchemy |
| **TOTAL** | | **~3.4 GB** | |

## Key Design Decisions

1. **No Ollama** — all models load directly via Python (llama-cpp-python, sentence-transformers, torchvision, NeMo). Eliminates the need for a separate Ollama daemon/installation.

2. **MedGemma GGUF** — 4-bit quantised medical LLM. Runs on CPU with `n_gpu_layers=0`. Medical-specialised (better than generic Gemma for health assessments).

3. **AI4Bharat IndicConformer** — IIT Madras model trained on 22 Indian languages. Far better for rural ASHA worker dialects than generic Whisper.

4. **Interactive Follow-up Loop** — If LLM confidence < 0.6, it generates 2-3 follow-up questions (max 3 rounds). Mimics how a real doctor probes for more information before concluding.

5. **rPPG** — Camera-based vital sign extraction (HR, RR, SpO2). No sensors needed — just a 10-15 second face video from a smartphone.

6. **Lazy Loading** — All heavy models are loaded on first use (not at startup), keeping initial startup fast and memory usage low until needed.

## File Structure
```
curebay backend/
├── main.py                     # FastAPI entry point
├── config.py                   # Centralised settings
├── setup.py                    # Auto-setup & model download
├── requirements.txt            # Python dependencies
├── routers/
│   ├── auth.py                 # JWT authentication
│   ├── patients.py             # Patient CRUD
│   └── assessment.py           # Assessment endpoints (text/voice/image/followup/rppg)
├── services/
│   ├── llm_service.py          # MedGemma GGUF via llama-cpp-python
│   ├── embedding_service.py    # MiniLM via sentence-transformers
│   ├── voice_service.py        # Sarvam AI + AI4Bharat IndicConformer
│   ├── image_service.py        # EfficientNetV2-Small classification
│   ├── rppg_service.py         # Camera-based vital signs
│   └── rag_service.py          # RAG pipeline (retrieve + prompt)
├── models/
│   ├── db_models.py            # SQLAlchemy ORM models
│   └── schemas.py              # Pydantic request/response schemas
├── database/
│   ├── sqlite_db.py            # SQLite connection & init
│   └── vector_db.py            # ChromaDB wrapper
├── data/
│   └── diseases_kb.py          # Disease knowledge base documents
└── models/
    └── medgemma/
        └── medgemma-1.5-4b-it-Q4_K_M.gguf  (downloaded by setup.py)
```
