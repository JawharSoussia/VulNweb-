"""Model Loading and Inference Utility"""
import pickle
import json
import logging
from pathlib import Path
from typing import Dict, Any, Tuple
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelPackage:
    """Manages model loading and versioning"""

    def __init__(self, model_dir: str = "ml_model/inference/models"):
        """Initialize model package"""
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)

        self.model = None
        self.preprocessor = None
        self.explainer = None
        self.metadata = None
        self.feature_names = None

    def load_model(self, model_name: str = "xgboost_smote_model.pkl"):
        """Load trained model"""
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
        """Make prediction"""
        if self.model is None:
            raise ValueError("Model not loaded. Call load_model() first.")

        # Make prediction
        pred = self.model.predict(X)
        pred_proba = self.model.predict_proba(X)

        # Threat score 0-100
        threat_score = float(pred_proba[0, 1] * 100)

        # Threat level
        if threat_score >= 70:
            threat_level = "critical"
        elif threat_score >= 30:
            threat_level = "suspicious"
        else:
            threat_level = "safe"

        return {
            'prediction': int(pred[0]),
            'threat_score': threat_score,
            'confidence': float(pred_proba[0, 1]),
            'threat_level': threat_level
        }

    def explain(self, X: np.ndarray, k: int = 3) -> list:
        """Get explanation"""
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