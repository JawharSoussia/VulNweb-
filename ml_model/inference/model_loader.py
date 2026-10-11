"""Model Loading and Inference Utility"""
import pickle
import json
import logging
from pathlib import Path
from typing import Dict, Any, Tuple
import numpy as np
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelPackage:
    """Manages model loading and versioning"""

    def __init__(self, model_dir: str = "ml_model/training/models",
                 backend: str | None = None):
        """Initialize model package"""
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)

        self.model = None
        self.preprocessor = None
        self.explainer = None
        self.metadata = None
        self.feature_names = None
        self.num_classes = 3
        self.backend = (backend or os.getenv("VULNWEB_MODEL_BACKEND", "xgboost")).lower()
        if self.backend not in {"xgboost", "pytorch"}:
            raise ValueError("VULNWEB_MODEL_BACKEND must be 'xgboost' or 'pytorch'")

    def load_model(self, model_name: str = "XGBoost_model.pkl"):
        """Load trained model"""
        if self.backend == "pytorch":
            from .pytorch_model import build_model
            import torch

            model_path = Path("ml_model/inference/models") / "pytorch_url_threat.pt"
            if not model_path.exists():
                raise FileNotFoundError(
                    f"PyTorch checkpoint not found: {model_path}. "
                    "Run ml_model/training/train_pytorch.py first."
                )
            checkpoint = torch.load(model_path, map_location="cpu", weights_only=True)
            self.model = build_model(
                checkpoint["input_features"], checkpoint["num_classes"]
            )
            self.model.load_state_dict(checkpoint["state_dict"])
            self.model.eval()
            self.scaler_mean = np.asarray(checkpoint["scaler_mean"], dtype=np.float32)
            self.scaler_scale = np.asarray(checkpoint["scaler_scale"], dtype=np.float32)
            return self.model

        model_path = self.model_dir / model_name

        if not model_path.exists():
            logger.error(f"Model not found: {model_path}")
            raise FileNotFoundError(f"Model not found: {model_path}")

        logger.info(f"Loading model from: {model_path}")
        with open(model_path, 'rb') as f:
            self.model = pickle.load(f)

        logger.info("✓ Model loaded successfully")
        return self.model

    def load_preprocessor(self, preprocessor_name: str = "preprocessor.pkl"):
        """Load preprocessor (scaler, encoder, etc.)"""
        if self.backend == "pytorch":
            return None
        preprocessor_path = Path("ml_model/training") / preprocessor_name

        if not preprocessor_path.exists():
            logger.warning(f"Preprocessor not found: {preprocessor_path}")
            return None

        logger.info(f"Loading preprocessor from: {preprocessor_path}")
        with open(preprocessor_path, 'rb') as f:
            self.preprocessor = pickle.load(f)

        logger.info("✓ Preprocessor loaded")
        return self.preprocessor

    def load_explainer(self, explainer_name: str = "shap_explainer.pkl"):
        """Load SHAP explainer"""
        explainer_path = Path("ml_model/inference") / explainer_name

        if not explainer_path.exists():
            logger.warning(f"Explainer not found: {explainer_path}")
            return None

        logger.info(f"Loading explainer from: {explainer_path}")
        try:
            with open(explainer_path, 'rb') as f:
                self.explainer = pickle.load(f)
            logger.info("✓ Explainer loaded")
        except (AttributeError, pickle.UnpicklingError) as e:
            logger.warning(f"Could not load explainer: {e}")
            return None

        return self.explainer

    def load_metadata(self, metadata_name: str = "model_metadata.json"):
        """Load model metadata"""
        if self.backend == "pytorch":
            metadata_path = Path("ml_model/inference/models/pytorch_url_threat_metadata.json")
        else:
            metadata_path = Path("ml_model/training/models") / metadata_name

        if not metadata_path.exists():
            logger.warning(f"Metadata not found: {metadata_path}")
            return None

        logger.info(f"Loading metadata from: {metadata_path}")
        with open(metadata_path, 'r') as f:
            self.metadata = json.load(f)

        self.feature_names = self.metadata.get('feature_names', [])
        logger.info(f"✓ Metadata loaded (Version: {self.metadata.get('model_name')})")
        return self.metadata

    def predict(self, X: np.ndarray) -> Dict[str, Any]:
        """Make prediction (multi-class)"""
        if self.model is None:
            raise ValueError("Model not loaded. Call load_model() first.")

        if self.backend == "pytorch":
            from .pytorch_model import predict_proba

            scaled = (X.astype(np.float32) - self.scaler_mean) / self.scaler_scale
            pred_proba = predict_proba(self.model, scaled)
            pred = np.argmax(pred_proba, axis=1)
        else:
            pred = self.model.predict(X)
            pred_proba = self.model.predict_proba(X)

        # Map class to threat score and level
        class_pred = int(pred[0])

        # Get max probability for confidence
        confidence = float(np.max(pred_proba[0]))

        # Map class to threat levels
        class_to_threat = {
            0: ("safe", 15.0),           # Safe: low threat score
            1: ("suspicious", 65.0),     # Threat Level 1: medium threat
            2: ("critical", 85.0)        # Threat Level 2: high threat
        }

        threat_level, threat_score = class_to_threat.get(class_pred, ("unknown", 50.0))

        return {
            'prediction': class_pred,
            'threat_score': threat_score,
            'confidence': confidence,
            'threat_level': threat_level,
            'probabilities': {
                'safe': float(pred_proba[0, 0]),
                'threat_level_1': float(pred_proba[0, 1]),
                'threat_level_2': float(pred_proba[0, 2])
            }
        }

    def explain(self, X: np.ndarray, k: int = 3) -> list:
        """Get explanation"""
        if self.backend == "pytorch":
            logger.info("SHAP explanations are not available for the PyTorch backend")
            return []
        if self.explainer is None:
            logger.warning("Explainer not loaded")
            return []

        # Get explanations (simplified)
        return self.explainer.batch_explain(X, k=k)

    def load_all(self):
        """Load all components"""
        logger.info("\n" + "=" * 60)
        logger.info("LOADING MODEL PACKAGE")
        logger.info("=" * 60)

        self.load_model()
        self.load_preprocessor()
        self.load_metadata()
        self.load_explainer()

        logger.info("\n✓ All components loaded successfully")
        return self


if __name__ == "__main__":
    # Test loading
    package = ModelPackage()
    package.load_all()

    # Verify
    print(f"Model: {package.model}")
    print(f"Metadata: {package.metadata}")