# ============================================================
# services/voice_service.py — Dual-Mode Voice Transcription
# ============================================================
# Online:  Sarvam AI Saaras v2 API (superior Indian language STT)
# Offline: AI4Bharat IndicConformer (22 Indian languages, MIT)
#
# Falls back automatically from API → local model when offline.
# Supports: hi, en, or, bn, te, ta, kn, ml, gu, mr, pa, as, etc.
# ============================================================

from pathlib import Path
from typing import Optional, Tuple
from loguru import logger

from config import settings


# Languages supported by AI4Bharat IndicConformer
SUPPORTED_LANGUAGES = {
    "hi": "Hindi",    "en": "English",  "or": "Odia",
    "bn": "Bengali",  "te": "Telugu",   "ta": "Tamil",
    "kn": "Kannada",  "ml": "Malayalam","gu": "Gujarati",
    "mr": "Marathi",  "pa": "Punjabi",  "as": "Assamese",
    "ur": "Urdu",     "sa": "Sanskrit", "ne": "Nepali",
    "sd": "Sindhi",   "kok": "Konkani", "doi": "Dogri",
    "mai": "Maithili","sat": "Santali", "mni": "Manipuri",
    "ks": "Kashmiri", "bo": "Bodo",
}


class VoiceService:
    """Dual-mode STT: Sarvam AI (online) + AI4Bharat IndicConformer (offline)."""

    def __init__(self):
        self._indic_model = None       # lazy loaded AI4Bharat model
        self._sarvam_available = bool(settings.SARVAM_API_KEY)

    # ── Public API ─────────────────────────────────────────────

    def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None,
    ) -> Tuple[str, str]:
        """
        Transcribe an audio file to text.

        Args:
            audio_path: Path to audio file (wav, mp3, m4a, ogg supported)
            language: ISO 639-1 language code (e.g. 'hi', 'en', 'or').

        Returns:
            Tuple of (transcribed_text, detected_language)
        """
        path = Path(audio_path)
        if not path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        # Try Sarvam API first (if configured and online)
        if self._sarvam_available:
            try:
                text, lang = self._transcribe_sarvam(str(path), language)
                logger.info(f"Transcribed via Sarvam AI: {len(text)} chars, lang={lang}")
                return text, lang
            except Exception as e:
                logger.warning(f"Sarvam API unavailable ({e}), falling back to IndicConformer")

        # Fallback: local AI4Bharat IndicConformer
        text, lang = self._transcribe_indic(str(path), language)
        logger.info(f"Transcribed via IndicConformer: {len(text)} chars, lang={lang}")
        return text, lang

    def transcribe_bytes(
        self,
        audio_bytes: bytes,
        filename: str,
        language: Optional[str] = None,
        save_dir: Optional[str] = None,
    ) -> Tuple[str, str]:
        """
        Transcribe audio from raw bytes (uploaded file).
        Saves temporarily to disk before transcription.
        """
        import tempfile
        import os

        suffix = Path(filename).suffix or ".wav"
        with tempfile.NamedTemporaryFile(
            suffix=suffix,
            delete=False,
            dir=save_dir,
        ) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        try:
            return self.transcribe(tmp_path, language=language)
        finally:
            os.unlink(tmp_path)

    # ── Sarvam AI (online mode) ────────────────────────────────

    def _transcribe_sarvam(
        self,
        audio_path: str,
        language: Optional[str] = None,
    ) -> Tuple[str, str]:
        """
        Sarvam AI Saaras v2 STT API call.
        Requires API key and internet connectivity.
        """
        import requests

        lang_code = language or settings.SARVAM_LANGUAGE_CODE

        with open(audio_path, "rb") as f:
            response = requests.post(
                settings.SARVAM_API_URL,
                headers={"api-subscription-key": settings.SARVAM_API_KEY},
                files={"file": (Path(audio_path).name, f, "audio/wav")},
                data={
                    "language_code": lang_code,
                    "model": "saaras:v2",
                },
                timeout=30,
            )

        if response.status_code != 200:
            raise RuntimeError(f"Sarvam API error {response.status_code}: {response.text[:200]}")

        result = response.json()
        transcript = result.get("transcript", "")
        detected_lang = result.get("language_code", lang_code)

        return transcript.strip(), detected_lang

    # ── AI4Bharat IndicConformer (offline mode) ────────────────

    def _load_indic_model(self):
        """Lazy load AI4Bharat IndicConformer model."""
        if self._indic_model is None:
            try:
                import nemo.collections.asr as nemo_asr
                logger.info(f"Loading AI4Bharat IndicConformer: {settings.INDIC_ASR_MODEL}")
                self._indic_model = nemo_asr.models.ASRModel.from_pretrained(
                    settings.INDIC_ASR_MODEL
                )
                logger.success("AI4Bharat IndicConformer loaded (22 Indian languages).")
            except ImportError:
                logger.error(
                    "nemo_toolkit not installed. Run: pip install nemo_toolkit[asr]"
                )
                raise
            except Exception as e:
                logger.error(f"Failed to load IndicConformer: {e}")
                raise

    def _transcribe_indic(
        self,
        audio_path: str,
        language: Optional[str] = None,
    ) -> Tuple[str, str]:
        """
        Local AI4Bharat IndicConformer transcription.
        Supports 22 Indian languages offline.
        """
        self._load_indic_model()

        lang_code = language if language in SUPPORTED_LANGUAGES else "hi"
        if language and language not in SUPPORTED_LANGUAGES:
            logger.warning(
                f"Unsupported language code '{language}', defaulting to Hindi. "
                f"Supported: {list(SUPPORTED_LANGUAGES.keys())}"
            )

        try:
            transcription = self._indic_model.transcribe([audio_path])

            # NeMo returns list or Hypothesis objects
            if isinstance(transcription, list):
                if len(transcription) > 0:
                    # Could be a list of strings or Hypothesis objects
                    text = transcription[0]
                    if hasattr(text, 'text'):
                        text = text.text
                else:
                    text = ""
            else:
                text = str(transcription)

            return text.strip(), lang_code

        except Exception as e:
            logger.error(f"IndicConformer transcription error: {e}")
            raise

    def is_available(self) -> bool:
        """Check if at least one STT backend is available."""
        if self._sarvam_available:
            return True
        try:
            self._load_indic_model()
            return True
        except Exception:
            return False


# Singleton
voice_service = VoiceService()
