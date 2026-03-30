# Model API Documentation

## Overview
Multi-class threat classification model for URL threat detection.

## Classes
- **0**: Safe URLs
- **1**: Threat Level 1 (Medium Risk)
- **2**: Threat Level 2 (High Risk)

## Input Features (37 total)
URL-based features including:
- url_length, domain_length, path_length
- num_colons, num_dots_in_domain, num_slashes
- Character ratios (uppercase, lowercase, digit, etc.)
- URL entropy and compression ratio
- And more...

## Model Performance
- **Accuracy**: 95.69%
- **F1-Score**: 0.9564
- **Precision**: 0.9564
- **Recall**: 0.9569

## Usage

### Python
```python
from classifier import ThreatClassifier
import pandas as pd

# Load model
clf = ThreatClassifier("models/XGBoost_model.pkl")

# Load data
X = pd.read_csv("features.csv")

# Predict
predictions = clf.predict(X)
probabilities = clf.predict_proba(X)

# Predict with confidence
results = clf.predict_with_confidence(X)
for result in results:
    print(f"Prediction: {result['prediction']}, Confidence: {result['confidence']:.4f}")
```

## Performance Notes
- Model achieves 95.69% accuracy on test set
- Best performance on Safe and Threat Level 1 classes
- Recommended for production deployment
