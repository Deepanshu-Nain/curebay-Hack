# ============================================================
# services/llm_service.py — LLM Inference
# ============================================================
# Primary:  MedGemma Q4_K_M GGUF via llama-cpp-python
# Fallback: Anthropic Claude API (when MEDGEMMA not downloaded)
#
# The fallback allows the system to work immediately out-of-the-box
# for demos, while MedGemma provides fully offline operation.
# ============================================================

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any
from loguru import logger

from config import settings


class LLMService:
    """
    Medical LLM inference.
    Primary:  MedGemma GGUF (offline, ~2.7 GB)
    Fallback: Claude claude-haiku-4-5 API (online, requires ANTHROPIC_API_KEY)
    """

    def __init__(self):
        self._model = None   # MedGemma model (lazy loaded)
        self._mode = None    # "medgemma" | "claude" | None

    # ── Health check ──────────────────────────────────────────

    def is_available(self) -> bool:
        """Check if any LLM backend is available."""
        # Check MedGemma first
        model_path = Path(settings.MEDGEMMA_MODEL_PATH)
        if model_path.exists():
            try:
                self._load_medgemma()
                return True
            except Exception:
                pass

        # Check Claude fallback
        if settings.ANTHROPIC_API_KEY:
            self._mode = "claude"
            return True

        return False

    def get_model_name(self) -> str:
        """Return the active model identifier."""
        if self._mode == "claude":
            return "claude-haiku-4-5 (fallback)"
        return "medgemma-1.5-4b-it-Q4_K_M"

    # ── Model loading ─────────────────────────────────────────

    def _load_medgemma(self):
        """Lazy load MedGemma GGUF model."""
        if self._model is not None:
            return
        model_path = settings.MEDGEMMA_MODEL_PATH
        if not Path(model_path).exists():
            raise FileNotFoundError(f"MedGemma not found at: {model_path}")
        try:
            from llama_cpp import Llama
            logger.info(f"Loading MedGemma GGUF: {model_path}")
            self._model = Llama(
                model_path=model_path,
                n_ctx=settings.MEDGEMMA_N_CTX,
                n_gpu_layers=settings.MEDGEMMA_N_GPU_LAYERS,
                verbose=False,
            )
            self._mode = "medgemma"
            logger.success("MedGemma model loaded.")
        except ImportError:
            raise RuntimeError("llama-cpp-python not installed. Run: pip install llama-cpp-python")

    def _ensure_backend(self):
        """Ensure a backend is available, selecting the best option."""
        if self._mode == "medgemma" and self._model:
            return  # Already loaded

        # Try MedGemma
        model_path = Path(settings.MEDGEMMA_MODEL_PATH)
        if model_path.exists():
            try:
                self._load_medgemma()
                return
            except Exception as e:
                logger.warning(f"MedGemma load failed: {e}")

        # Fall back to Claude API
        if settings.ANTHROPIC_API_KEY:
            self._mode = "claude"
            logger.info("Using Claude API as LLM backend.")
            return

        raise RuntimeError(
            "No LLM backend available. Either:\n"
            "1. Download MedGemma: python setup.py\n"
            "2. Set ANTHROPIC_API_KEY in .env for Claude fallback"
        )

    # ── Text inference ────────────────────────────────────────

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = None,
        max_tokens: int = None,
    ) -> str:
        """
        Run text inference. Uses MedGemma if available, else Claude API.
        Returns raw text response.
        """
        self._ensure_backend()

        temp = temperature if temperature is not None else settings.MEDGEMMA_TEMPERATURE
        tokens = max_tokens if max_tokens is not None else settings.MEDGEMMA_MAX_TOKENS

        if self._mode == "medgemma":
            return self._generate_medgemma(prompt, system_prompt, temp, tokens)
        else:
            return self._generate_claude(prompt, system_prompt, temp, tokens)

    def _generate_medgemma(self, prompt, system_prompt, temperature, max_tokens):
        """Generate using local MedGemma GGUF."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        try:
            response = self._model.create_chat_completion(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=0.9,
            )
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"MedGemma generate error: {e}")
            raise

    def _generate_claude(self, prompt, system_prompt, temperature, max_tokens):
        """Generate using Anthropic Claude API as fallback."""
        import anthropic

        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

        sys_msg = system_prompt or (
            "You are CureBay AI, a medical decision-support assistant for rural ASHA "
            "workers in India. You provide preliminary health assessments to help frontline "
            "health workers triage patients. You always respond with valid JSON as instructed."
        )

        try:
            message = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=min(max_tokens, 2048),
                temperature=temperature,
                system=sys_msg,
                messages=[{"role": "user", "content": prompt}],
            )
            return message.content[0].text
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            raise

    # ── JSON response parsing ─────────────────────────────────

    def parse_json_response(self, raw: str) -> Dict[str, Any]:
        """Extract and parse JSON from LLM response."""
        text = raw.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])

        start = text.find("{")
        end = text.rfind("}") + 1
        if start == -1 or end == 0:
            raise ValueError(f"No JSON object found in LLM response: {raw[:200]}")

        json_str = text[start:end]
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}\nRaw: {json_str[:300]}")
            raise


# Singleton
llm_service = LLMService()
