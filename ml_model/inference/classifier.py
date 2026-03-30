"""Model Inference Wrapper"""
import pickle
import pandas as pd
import numpy as np
from pathlib import Path

class ThreatClassifier:
    """Production inference wrapper for threat classification model"""

    def __init__(self, model_path):
        """Load pre-trained model"""
        with open(model_path, 'rb') as f:
            self.model = pickle.load(f)
        self.class_names = ["Safe", "Threat Level 1", "Threat Level 2"]

    def predict(self, X):
        """Predict threat class"""
        return self.model.predict(X)

    def predict_proba(self, X):
        """Predict class probabilities"""
        return self.model.predict_proba(X)

    def predict_with_confidence(self, X):
        """Predict with confidence scores"""
        predictions = self.model.predict(X)
        probabilities = self.model.predict_proba(X)

        results = []
        for idx, pred in enumerate(predictions):
            confidence = probabilities[idx][pred]
            results.append({
                'prediction': self.class_names[pred],
                'confidence': float(confidence),
                'probabilities': {
                    self.class_names[i]: float(probabilities[idx][i])
                    for i in range(len(self.class_names))
                }
            })

        return results

if __name__ == "__main__":
    # Example usage
    classifier = ThreatClassifier("ml_model/training/models/XGBoost_model.pkl")

    # Load sample data
    test_df = pd.read_csv("data/test/test_processed.csv").head(5)
    X_test = test_df.drop(columns=['threat_level'])

    # Predict with confidence
    results = classifier.predict_with_confidence(X_test)

    for idx, result in enumerate(results):
        print(f"Sample {idx + 1}:")
        print(f"  Prediction: {result['prediction']}")
        print(f"  Confidence: {result['confidence']:.4f}")
        print(f"  Probabilities: {result['probabilities']}")
        print()
