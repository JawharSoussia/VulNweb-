"""High-level prediction interface"""
import numpy as np
import pandas as pd
from .model_loader import ModelPackage
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Predictor:
    """High-level prediction interface"""

    def __init__(self):
        """Initialize predictor"""
        self.package = ModelPackage()
        self.package.load_all()

    def predict_batch(self, feature_list: list) -> list:
        """Predict on batch of feature vectors"""
        X = np.array(feature_list).reshape(len(feature_list), -1)
        results = []

        for i in range(len(X)):
            pred = self.package.predict(X[i:i+1])
            exp = self.package.explain(X[i:i+1])
            results.append({
                **pred,
                'explanation': exp[0] if exp else []
            })

        return results

    def predict_single(self, features: dict) -> dict:
        """Predict on single sample"""
        # Convert features to array in correct order
        feature_array = np.array([
            features.get(fname, 0) for fname in self.package.feature_names
        ]).reshape(1, -1)

        result = self.package.predict(feature_array)
        explanation = self.package.explain(feature_array)

        return {
            **result,
            'explanation': explanation[0] if explanation else []
        }


if __name__ == "__main__":
    predictor = Predictor()

    # Test prediction
    sample_features = {fname: np.random.randn() for fname in predictor.package.feature_names}
    result = predictor.predict_single(sample_features)

    print(f"Prediction: {result}")