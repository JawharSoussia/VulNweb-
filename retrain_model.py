"""Retrain model with improved features for better threat detection"""
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import logging
from sklearn.preprocessing import RobustScaler

# Add paths
sys.path.insert(0, str(Path(__file__).parent))

from backend.app.feature_extractor import URLFeatureExtractor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def map_labels_to_threat_level(df):
    """Map original labels to threat levels"""
    if 'threat_level' in df.columns:
        return df

    label_mapping = {
        'benign': 0,
        'defacement': 1,
        'phishing': 2,
        'malware': 2
    }

    if 'type' in df.columns:
        df['threat_level'] = df['type'].str.lower().map(label_mapping)
        return df
    elif 'label' in df.columns:
        df['threat_level'] = df['label'].map(label_mapping)
        return df
    else:
        logger.error("No label column found")
        return None

def retrain_with_new_features():
    """
    Retrain the model using the updated feature extractor with:
    - is_shortener_url
    - has_executable_extension
    - has_redirect_parameter
    """

    # Load raw training data
    train_csv = Path("data/train/train.csv")
    if not train_csv.exists():
        logger.error(f"Training data not found: {train_csv}")
        return False

    logger.info("Loading raw training data...")
    train_df = pd.read_csv(train_csv)
    logger.info(f"Loaded {len(train_df)} samples")

    # Map labels to threat levels
    train_df = map_labels_to_threat_level(train_df)
    if train_df is None:
        return False

    # Extract URLs
    if 'url' not in train_df.columns:
        logger.error("No 'url' column found in training data")
        return False

    # Initialize feature extractor
    extractor = URLFeatureExtractor()

    logger.info(f"Extracting {len(extractor.FEATURE_NAMES)} features from URLs...")

    # Extract features for each URL
    feature_list = []
    valid_indices = []

    for idx, row in train_df.iterrows():
        if idx % 1000 == 0:
            logger.info(f"Processing {idx}/{len(train_df)}...")

        url = row['url']
        try:
            features = extractor.extract(url)[0]
            feature_list.append(features)
            valid_indices.append(idx)
        except Exception as e:
            logger.warning(f"Error extracting features for URL {url}: {e}")

    # Create new dataframe with extracted features
    features_df = pd.DataFrame(
        feature_list,
        columns=extractor.FEATURE_NAMES
    )

    # Add target column from valid indices
    threat_levels = train_df.iloc[valid_indices]['threat_level'].values
    features_df['threat_level'] = threat_levels

    logger.info(f"Extracted features shape: {features_df.shape}")
    logger.info(f"New features included: is_shortener_url, has_executable_extension, has_redirect_parameter")

    # Check for missing values
    if features_df.isnull().any().any():
        logger.warning(f"Found NaN values, filling with 0")
        features_df = features_df.fillna(0)

    # Save raw (unscaled) training data
    raw_output_path = Path("data/train/train_features_raw_v2.csv")
    raw_output_path.parent.mkdir(parents=True, exist_ok=True)
    features_df.to_csv(raw_output_path, index=False)
    logger.info(f"Saved raw features to {raw_output_path}")

    # Scale features (excluding threat_level)
    scaler = RobustScaler()
    feature_cols = [col for col in features_df.columns if col != 'threat_level']
    features_df[feature_cols] = scaler.fit_transform(features_df[feature_cols])

    # Save scaled training data
    scaled_output_path = Path("data/train/train_processed.csv")
    features_df.to_csv(scaled_output_path, index=False)
    logger.info(f"Saved scaled features to {scaled_output_path}")

    # Train models
    logger.info("\n" + "="*70)
    logger.info("TRAINING MODELS WITH NEW FEATURES")
    logger.info("="*70)

    from ml_model.training.train import ModelTrainer

    trainer = ModelTrainer(features_df, target_col='threat_level')
    best_model, results, importance = trainer.train_all_models()

    # Save best model
    output_dir = Path("ml_model/training/models")
    output_dir.mkdir(exist_ok=True)

    model_path = output_dir / f"{trainer.best_model_name}_model.pkl"
    import pickle
    with open(model_path, 'wb') as f:
        pickle.dump(best_model, f)

    logger.info(f"\n✓ New model saved to: {model_path}")
    logger.info(f"✓ Model type: {trainer.best_model_name}")

    # Update model metadata
    import json
    from datetime import datetime

    metadata = {
        'model_name': trainer.best_model_name,
        'version': '2.0.0',
        'trained_at': datetime.now().isoformat(),
        'cv_results': {k: {mk: float(mv) if isinstance(mv, np.ndarray) else mv
                          for mk, mv in v.items()}
                       for k, v in results.items()},
        'feature_names': extractor.FEATURE_NAMES,
        'target_col': 'threat_level',
        'improved_features': [
            'is_shortener_url (detects bit.ly, tinyurl, etc)',
            'has_executable_extension (detects .exe, .dll, etc)',
            'has_redirect_parameter (detects redirect parameters)'
        ]
    }

    metadata_path = output_dir / "model_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    logger.info(f"✓ Metadata saved to: {metadata_path}")
    logger.info("\n" + "="*70)
    logger.info("RETRAINING COMPLETE - Ready for testing!")
    logger.info("="*70)

    return True

if __name__ == "__main__":
    success = retrain_with_new_features()
    sys.exit(0 if success else 1)

