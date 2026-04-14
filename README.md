# CureBay AI Health Assistant Backend

Offline-first FastAPI backend for multimodal health assessment workflows used by frontline health workers.

## Highlights

- Offline-capable architecture (no Ollama dependency)
- RAG pipeline over a local disease knowledge base (ChromaDB + MiniLM embeddings)
- MedGemma GGUF inference via `llama-cpp-python`
- Multimodal assessment:
  - text symptoms
  - voice input (Sarvam API with offline fallback path)
  - image-assisted assessment
  - rPPG vitals from short face video
- Interactive follow-up question loop for low-confidence cases
- SQLite-backed auth, patient records, vitals, and assessment history

## Tech Stack

- Python 3.10-3.13 (3.11/3.12 recommended)
- FastAPI + Uvicorn
- SQLAlchemy + SQLite
- ChromaDB
- Sentence Transformers (`all-MiniLM-L6-v2`)
- `llama-cpp-python` (MedGemma GGUF)
- Torch / Torchvision (image pipeline)
- OpenCV + SciPy (rPPG)

## Project Structure

```text
curebay backend/
├── main.py
├── config.py
├── setup.py
├── requirements.txt
├── routers/
│   ├── auth.py
│   ├── patients.py
│   └── assessment.py
├── services/
├── models/
├── database/
├── data/
└── uploads/
```

## Quick Start

### 1. Clone

```bash
git clone https://github.com/Deepanshu-Nain/curebay-Hack.git
cd curebay-Hack
```

### 2. Create and activate virtual environment

Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

Optional offline STT (AI4Bharat IndicConformer via NeMo):

```bash
pip install "nemo_toolkit[asr]>=1.22.0"
```

Note: the NeMo offline STT package is optional, works best on Python 3.10-3.12, and may need Microsoft C++ Build Tools on Windows.

### 4. Run setup (recommended)

```bash
python setup.py
```

This script can:

- validate environment
- install missing dependencies
- download MedGemma GGUF model (if missing)
- warm up embedding model
- initialize SQLite database

### 5. Start API server

If setup does not auto-start:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Docs:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Health: `http://localhost:8000/health`

## API Overview

### Auth (`/auth`)

- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`
- `PUT /auth/me`
- `POST /auth/change-password`

### Patients (`/patients`)

- `POST /patients/`
- `GET /patients/`
- `GET /patients/{patient_id}`
- `PUT /patients/{patient_id}`
- `DELETE /patients/{patient_id}`
- `POST /patients/{patient_id}/vitals`
- `GET /patients/{patient_id}/vitals`

### Assessment (`/assessment`)

- `POST /assessment/text`
- `POST /assessment/voice`
- `POST /assessment/image`
- `POST /assessment/followup`
- `POST /assessment/rppg-vitals`
- `GET /assessment/session/{session_id}`
- `GET /assessment/patient/{patient_id}`
- `GET /assessment/{assessment_id}`

## Configuration

Core settings are defined in `config.py` and can be overridden with environment variables via a `.env` file.

Important values:

- `SECRET_KEY`
- `SARVAM_API_KEY` (optional for online STT)
- `MEDGEMMA_MODEL_PATH`
- `CHROMA_PERSIST_DIR`

## Notes for Contributors

- Large runtime artifacts (models, DB, logs, uploads, venv) are ignored via `.gitignore`.
- Do not commit secrets or API keys.
- Prefer running `python setup.py --check` before opening a PR.

## License

No license file is currently provided. Add a `LICENSE` file if you want to publish with explicit usage terms.
