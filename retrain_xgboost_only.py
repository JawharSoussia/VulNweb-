"""Quick retraining with just XGBoost and 40 improved features"""
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import logging
from sklearn.preprocessing import RobustScaler
from xgboost import XGBClassifier
import pickle
import json
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from backend.app.feature_extractor import URLFeatureExtractor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def quick_retrain():
    """Quick retrain with XGBoost only"""

    # Load raw training data
    train_csv = Path("data/train/train.csv")
    logger.info(f"Loading training data from {train_csv}")
    train_df = pd.read_csv(train_csv)
    logger.info(f"Loaded {len(train_df)} samples")

    # Map labels to threat levels
    label_mapping = {
        'benign': 0,
        'defacement': 1,
        'phishing': 2,
        'malware': 2
    }

    train_df['threat_level'] = train_df['type'].str.lower().map(label_mapping)

    # Initialize feature extractor
    extractor = URLFeatureExtractor()
    logger.info(f"Extracting {len(extractor.FEATURE_NAMES)} features...")

    # Extract features
    feature_list = []
    for idx, row in train_df.iterrows():
        if idx % 50000 == 0:
            logger.info(f"Processing {idx}/{len(train_df)}...")

        try:
            features = extractor.extract(row['url'])[0]
            feature_list.append(features)
        except:
            pass

    # Create dataframe
    features_df = pd.DataFrame(feature_list, columns=extractor.FEATURE_NAMES)
    features_df['threat_level'] = train_df['threat_level'].iloc[:len(features_df)].values

    logger.info(f"Features extracted: {features_df.shape}")

    # Separate X and y
    X = features_df.drop(columns=['threat_level'])
    y = features_df['threat_level']

    # Scale features
    scaler = RobustScaler()
    X_scaled = pd.DataFrame(scaler.fit_transform(X), columns=X.columns)

    # Train XGBoost
    logger.info("\nTraining XGBoost with 40 features...")
    model = XGBClassifier(
        n_estimators=200,
        max_depth=7,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        n_jobs=-1,
        objective='multi:softmax',
        num_class=3
    )

    model.fit(X_scaled, y)

    # Save model
    output_dir = Path("ml_model/training/models")
    model_path = output_dir / "XGBoost_model.pkl"

    with open(model_path, 'wb') as f:
        pickle.dump(model, f)

    logger.info(f"Model saved to {model_path}")

    # Save metadata
    metadata = {
        'model_name': 'XGBoost',
        'version': '2.0.0',
        'trained_at': datetime.now().isoformat(),
        'feature_count': len(extractor.FEATURE_NAMES),
        'feature_names': extractor.FEATURE_NAMES,
        'improved_features': [
            'is_shortener_url - Detects URL shorteners',
            'has_executable_extension - Detects .exe, .dll, etc',
            'has_redirect_parameter - Detects redirect params'
        ]
    }

    metadata_path = output_dir / "model_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    logger.info(f"✓ Metadata saved: {metadata_path}")
    logger.info("\n✓ RETRAINING COMPLETE - v2.0.0 with 40 features ready!")

if __name__ == "__main__":
    quick_retrain()
