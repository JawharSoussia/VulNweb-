"""Direct test of threat boost logic"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from backend.app.feature_extractor import URLFeatureExtractor
from ml_model.inference import ModelPackage
import json

def predict_with_boost(url):
    """Make prediction with threat boost"""

    extractor = URLFeatureExtractor()
    model_pkg = ModelPackage()
    model_pkg.load_all()

    # Extract features
    X = extractor.extract(url)

    # Extract new threat features
    new_threat_features = {
        'is_shortener_url': X[0, -3],
        'has_executable_extension': X[0, -2],
        'has_redirect_parameter': X[0, -1]
    }

    # Use only first 37 for model
    X_model = X[:, :37]
    prediction = model_pkg.predict(X_model)

    # Original scores
    threat_score = prediction['threat_score']
    threat_level = prediction['threat_level']
    predicted_class = prediction['prediction']

    # Calculate boost
    threat_boost = 0
    threat_indicators = []

    if new_threat_features['is_shortener_url'] > 0.5:
        threat_boost += 25
        threat_indicators.append("URL shortened (bit.ly, tinyurl, etc.)")

    if new_threat_features['has_executable_extension'] > 0.5:
        threat_boost += 30
        threat_indicators.append("Executable file download detected (.exe, .dll, etc.)")

    if new_threat_features['has_redirect_parameter'] > 0.5:
        threat_boost += 20
        threat_indicators.append("Redirect parameter detected in URL")

    # Apply boost
    if threat_boost > 0:
        threat_score = min(100, threat_score + threat_boost)
        if threat_score >= 67 and predicted_class < 2:
            threat_level = "critical"
            predicted_class = 2
        elif threat_score >= 34 and predicted_class < 1:
            threat_level = "suspicious"
            predicted_class = 1

    return {
        'url': url,
        'base_score': prediction['threat_score'],
        'threat_score': threat_score,
        'threat_level': threat_level,
        'predicted_class': predicted_class,
        'threat_boost': threat_boost,
        'indicators': threat_indicators
    }

# Test URLs
test_urls = [
    'https://bit.ly/abc123',
    'https://example.com/download?file=random.exe',
    'https://example.com/admin/login.php?redirect=http://evil.com'
]

print("Testing threat boost logic:")
print("=" * 80)

for url in test_urls:
    result = predict_with_boost(url)
    print(f"\nURL: {url}")
    print(f"  Base score: {result['base_score']:.1f} -> New score: {result['threat_score']:.1f}")
    print(f"  Threat level: {result['threat_level']} (class: {result['predicted_class']})")
    print(f"  Boost: +{result['threat_boost']}")
    if result['indicators']:
        for indicator in result['indicators']:
            print(f"    * {indicator}")
