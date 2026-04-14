# ============================================================
# services/image_service.py — Medical Image Classification
# ============================================================
# Uses EfficientNetV2-Small (torchvision, ~20 MB) for image
# classification. Converts image predictions to text descriptions
# suitable for the RAG pipeline.
#
# Replaces ollama_service.describe_image() — no LLM needed for
# initial image analysis. Much faster and lighter.
# ============================================================

from pathlib import Path
from typing import Dict, List, Any
from loguru import logger

from config import settings


# Medical-relevant ImageNet class mappings (subset)
# These map ImageNet class indices to medically relevant descriptions
MEDICAL_KEYWORDS = {
    "skin": ["rash", "lesion", "wound", "infection", "dermatitis", "eczema",
             "psoriasis", "burn", "bruise", "ulcer", "abscess"],
    "respiratory": ["chest", "lung", "x-ray", "xray"],
    "eye": ["eye", "conjunctivitis", "cataract", "redness"],
    "oral": ["mouth", "teeth", "gum", "throat", "tongue"],
}


class ImageService:
    """EfficientNetV2-Small medical image classification."""

    def __init__(self):
        self._model = None
        self._transform = None
        self._categories = None

    def _load_model(self):
        """Lazy load EfficientNetV2-Small and ImageNet categories."""
        if self._model is not None:
            return

        try:
            import torch
            import torchvision.models as models
            import torchvision.transforms as transforms

            logger.info("Loading EfficientNetV2-Small for image classification...")

            # Load pre-trained model
            weights = models.EfficientNet_V2_S_Weights.DEFAULT
            self._model = models.efficientnet_v2_s(weights=weights)
            self._model.eval()

            # Get the preprocessing transform from the weights
            self._transform = weights.transforms()

            # Get ImageNet categories
            self._categories = weights.meta["categories"]

            logger.success(f"EfficientNetV2-Small loaded ({len(self._categories)} categories)")

        except ImportError:
            logger.error("torch/torchvision not installed. Run: pip install torch torchvision")
            raise
        except Exception as e:
            logger.error(f"Failed to load EfficientNetV2: {e}")
            raise

    def classify_image(self, image_path: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Classify an image and return top-K predictions with confidence scores.

        Args:
            image_path: Path to the image file
            top_k: Number of top predictions to return

        Returns:
            Dict with predictions list, top label, and confidence
        """
        self._load_model()
        import torch
        from PIL import Image

        img_path = Path(image_path)
        if not img_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        # Load and preprocess image
        img = Image.open(img_path).convert("RGB")
        tensor = self._transform(img).unsqueeze(0)

        # Run inference
        with torch.no_grad():
            outputs = self._model(tensor)
            probs = torch.softmax(outputs, dim=1)
            top_probs, top_indices = torch.topk(probs, top_k)

        predictions = []
        for prob, idx in zip(top_probs[0], top_indices[0]):
            predictions.append({
                "label": self._categories[idx.item()],
                "confidence": round(prob.item(), 4),
                "index": idx.item(),
            })

        return {
            "predictions": predictions,
            "top_label": predictions[0]["label"] if predictions else "unknown",
            "top_confidence": predictions[0]["confidence"] if predictions else 0.0,
        }

    def describe_image(self, image_path: str) -> str:
        """
        Generate a text description of an image for the RAG pipeline.
        Converts EfficientNet classification results into natural language
        suitable for embedding and LLM prompting.

        This replaces ollama_service.describe_image().
        """
        try:
            result = self.classify_image(image_path, top_k=5)
        except Exception as e:
            logger.error(f"Image classification failed: {e}")
            return "Unable to analyse image. Manual inspection required."

        predictions = result["predictions"]
        top_label = result["top_label"]
        top_conf = result["top_confidence"]

        # Build natural language description
        description_parts = []

        # Primary classification
        description_parts.append(
            f"Image analysis detected: {top_label} (confidence: {top_conf:.0%})."
        )

        # Additional predictions
        if len(predictions) > 1:
            other_labels = [
                f"{p['label']} ({p['confidence']:.0%})"
                for p in predictions[1:3]
                if p['confidence'] > 0.05
            ]
            if other_labels:
                description_parts.append(
                    f"Other possible classifications: {', '.join(other_labels)}."
                )

        # Medical context hints
        all_labels = " ".join(p["label"].lower() for p in predictions)
        medical_hints = []
        for category, keywords in MEDICAL_KEYWORDS.items():
            if any(kw in all_labels for kw in keywords):
                medical_hints.append(category)

        if medical_hints:
            description_parts.append(
                f"Potentially relevant medical category: {', '.join(medical_hints)}."
            )
        else:
            description_parts.append(
                "Image does not appear to match known medical categories. "
                "Clinical examination recommended."
            )

        description_parts.append(
            "Note: This is automated image classification, not medical diagnosis. "
            "Clinical assessment by a healthcare professional is recommended."
        )

        return " ".join(description_parts)

    def is_available(self) -> bool:
        """Check if the image classification model can be loaded."""
        try:
            self._load_model()
            return True
        except Exception:
            return False


# Singleton
image_service = ImageService()
