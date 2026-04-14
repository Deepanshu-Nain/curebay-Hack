# ============================================================
# services/llm_service.py — LLM Inference via MedGemma GGUF
# ============================================================
# Replaces ollama_service.py. Uses llama-cpp-python to load
# MedGemma-1.5-4b-it-Q4_K_M.gguf directly — no Ollama needed.
#
# Model: ~2.7 GB, medical-specialised, 4-bit quantised.
# Runs on CPU (n_gpu_layers=0) for Android/low-spec devices.
# ============================================================

import json
from pathlib import Path
from typing import Optional, Dict, Any
from loguru import logger

from config import settings


class LLMService:
    """MedGemma GGUF inference via llama-cpp-python."""

    def __init__(self):
        self._model = None   # lazy loaded

    def _load_model(self):
        """Lazy load MedGemma GGUF model on first use."""
        if self._model is None:
            model_path = settings.MEDGEMMA_MODEL_PATH
            if not Path(model_path).exists():
                raise FileNotFoundError(
                    f"MedGemma GGUF model not found at: {model_path}\n"
                    f"Run: python setup.py  (to auto-download)"
                )
            try:
                from llama_cpp import Llama
                logger.info(f"Loading MedGemma GGUF model: {model_path}")
                self._model = Llama(
                    model_path=model_path,
                    n_ctx=settings.MEDGEMMA_N_CTX,
                    n_gpu_layers=settings.MEDGEMMA_N_GPU_LAYERS,
                    verbose=False,
                )
                logger.success("MedGemma model loaded successfully.")
            except ImportError:
                logger.error("llama-cpp-python not installed. Run: pip install llama-cpp-python")
                raise
            except Exception as e:
                logger.error(f"Failed to load MedGemma model: {e}")
                raise

    # ── Health check ───────────────────────────────────────────

    def is_available(self) -> bool:
        """Check if the MedGemma GGUF file exists and can be loaded."""
        model_path = Path(settings.MEDGEMMA_MODEL_PATH)
        if not model_path.exists():
            logger.warning(f"MedGemma model not found: {model_path}")
            return False
        try:
            self._load_model()
            return True
        except Exception as e:
            logger.error(f"MedGemma unavailable: {e}")
            return False

    # ── Text inference ─────────────────────────────────────────

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = None,
        max_tokens: int = None,
    ) -> str:
        """
        Run text inference with MedGemma.
        Returns raw text response.
        """
        self._load_model()

        temp = temperature if temperature is not None else settings.MEDGEMMA_TEMPERATURE
        tokens = max_tokens if max_tokens is not None else settings.MEDGEMMA_MAX_TOKENS

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self._model.create_chat_completion(
                messages=messages,
                temperature=temp,
                max_tokens=tokens,
                top_p=0.9,
            )
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"MedGemma generate error: {e}")
            raise

    # ── JSON response parsing ──────────────────────────────────

    def parse_json_response(self, raw: str) -> Dict[str, Any]:
        """
        Extract and parse JSON from LLM response.
        Handles cases where the model wraps JSON in markdown code blocks.
        """
        # Strip markdown fences if present
        text = raw.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            # Remove first and last fence lines
            text = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])

        # Find first { and last }
        start = text.find("{")
        end   = text.rfind("}") + 1
        if start == -1 or end == 0:
            raise ValueError(f"No JSON object found in LLM response: {raw[:200]}")

        json_str = text[start:end]
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}\nRaw: {json_str[:300]}")
            raise

    def get_model_name(self) -> str:
        """Return the model identifier for logging/storage."""
        return "medgemma-1.5-4b-it-Q4_K_M"


# Singleton
llm_service = LLMService()
