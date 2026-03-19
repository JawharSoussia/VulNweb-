"""Data Splitting for UNSW-NB15 Dataset

Splits the raw UNSW-NB15 dataset into train/val/test sets.
Ratios: 70% train, 15% val, 15% test (stratified by label)
"""
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
DATA_RAW_PATH = Path("data/raw")
DATA_PROCESSED_PATH = Path("data/processed")
DATA_TRAIN_PATH = Path("data/train")
DATA_VAL_PATH = Path("data/val")
DATA_TEST_PATH = Path("data/test")

# Create output directories
DATA_TRAIN_PATH.mkdir(exist_ok=True)
DATA_VAL_PATH.mkdir(exist_ok=True)
DATA_TEST_PATH.mkdir(exist_ok=True)

# UNSW-NB15 Column Names (Kaggle version has 49 columns with 2 extra at start)
UNSW_COLUMNS = [
    'Unnamed_0', 'Unnamed_1',  # Extra columns in Kaggle version
    'srcip', 'sport', 'dstip', 'dstp', 'proto', 'state', 'dur', 'sbytes', 'dbytes',
    'sttl', 'dttl', 'sloss', 'dloss', 'service', 'sload', 'dload', 'spkts', 'dpkts',
    'swin', 'dwin', 'stcpb', 'dtcpb', 'smeansz', 'dmeansz', 'sjit', 'djit',
    'stime', 'ltime', 'sintpkt', 'dintpkt', 'tcprtt', 'synack', 'ackdat',
    'is_sm_ips_ports', 'ct_state_ttl', 'ct_flw_http_mthd', 'is_ftp_login',
    'ct_ftp_cmd', 'ct_srv_src', 'ct_srv_dst', 'ct_dst_ltm', 'ct_src_ltm',
    'ct_src_dport_ltm', 'ct_dst_sport_ltm', 'ct_dst_src_ltm', 'attack', 'label'
]


def load_unsw_data():
    """Load all UNSW-NB15 CSV files"""
    logger.info("Loading UNSW-NB15 dataset files...")
    from glob import glob

    csv_files = sorted(glob(str(DATA_RAW_PATH / "*.csv")))

    if not csv_files:
        logger.error("No CSV files found in data/raw/")
        raise FileNotFoundError("Please download UNSW-NB15 dataset to data/raw/")

    # Load all CSV files
    df_list = []
    for csv_file in csv_files:
        logger.info(f"Loading: {Path(csv_file).name}")
        df = pd.read_csv(csv_file, names=UNSW_COLUMNS, low_memory=False)

        # Drop the extra Kaggle index columns
        df = df.drop(['Unnamed_0', 'Unnamed_1'], axis=1, errors='ignore')

        # Convert numeric columns
        numeric_cols = [col for col in df.columns
                       if col not in ['srcip', 'dstip', 'service', 'state', 'proto', 'attack', 'label']]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # Ensure proto is string
        df['proto'] = df['proto'].astype(str).str.lower().fillna('unknown')

        df_list.append(df)

    # Combine all files
    df = pd.concat(df_list, ignore_index=True)
    logger.info(f"✓ Loaded UNSW-NB15 dataset: {df.shape}")

    return df


def split_data(df, train_ratio=0.70, val_ratio=0.15, test_ratio=0.15, random_state=42):
    """Split data into train/val/test stratified by label"""
    logger.info("\n" + "=" * 60)
    logger.info("DATA SPLITTING")
    logger.info("=" * 60)

    logger.info(f"Original dataset: {df.shape}")

    # Remove rows with missing labels (needed for training)
    if 'label' in df.columns:
        missing_labels = df['label'].isna().sum()
        if missing_labels > 0:
            logger.warning(f"Removing {missing_labels:,} rows with missing labels ({missing_labels/len(df)*100:.2f}%)")
            df = df[df['label'].notna()].copy()
            logger.info(f"Dataset after removing missing labels: {df.shape}")

    # Verify ratios
    total_ratio = train_ratio + val_ratio + test_ratio
    if abs(total_ratio - 1.0) > 0.001:
        logger.warning(f"Ratios sum to {total_ratio}, normalizing...")
        train_ratio = train_ratio / total_ratio
        val_ratio = val_ratio / total_ratio
        test_ratio = test_ratio / total_ratio

    logger.info(f"Split ratios: train={train_ratio:.1%}, val={val_ratio:.1%}, test={test_ratio:.1%}")

    # Check if label column exists
    if 'label' not in df.columns:
        logger.warning("⚠️  'label' column not found, splitting without stratification")
        stratify = None
    else:
        stratify = df['label']
        logger.info(f"Stratifying by 'label' column")

    # First split: train+val vs test
    train_val, test = train_test_split(
        df,
        test_size=test_ratio,
        random_state=random_state,
        stratify=stratify
    )

    # Second split: train vs val
    train, val = train_test_split(
        train_val,
        test_size=val_ratio / (train_ratio + val_ratio),
        random_state=random_state,
        stratify=train_val['label'] if 'label' in train_val.columns else None
    )

    logger.info(f"✓ Train set: {train.shape}")
    logger.info(f"✓ Val set: {val.shape}")
    logger.info(f"✓ Test set: {test.shape}")

    # Log class distribution for each split
    if 'label' in df.columns:
        logger.info("\n" + "=" * 60)
        logger.info("CLASS DISTRIBUTION PER SPLIT")
        logger.info("=" * 60)
        for name, split_df in [('Train', train), ('Val', val), ('Test', test)]:
            label_dist = split_df['label'].value_counts(normalize=True) * 100
            logger.info(f"\n{name}:")
            for label, pct in label_dist.items():
                logger.info(f"  Label {int(label)}: {pct:.2f}%")

    return train, val, test


def save_splits(train, val, test):
    """Save split data to CSV files"""
    logger.info("\n" + "=" * 60)
    logger.info("SAVING SPLITS")
    logger.info("=" * 60)

    # Save train
    train_path = DATA_TRAIN_PATH / "train.csv"
    train.to_csv(train_path, index=False)
    logger.info(f"✓ Saved: {train_path} ({train.shape[0]:,} rows)")

    # Save val
    val_path = DATA_VAL_PATH / "val.csv"
    val.to_csv(val_path, index=False)
    logger.info(f"✓ Saved: {val_path} ({val.shape[0]:,} rows)")

    # Save test
    test_path = DATA_TEST_PATH / "test.csv"
    test.to_csv(test_path, index=False)
    logger.info(f"✓ Saved: {test_path} ({test.shape[0]:,} rows)")

    logger.info("\n" + "=" * 60)
    logger.info("✓ DATA SPLITTING COMPLETE")
    logger.info("=" * 60)


if __name__ == "__main__":
    try:
        # Load data
        df = load_unsw_data()

        # Split data
        train, val, test = split_data(df)

        # Save splits
        save_splits(train, val, test)

    except Exception as e:
        logger.error(f"Data splitting failed: {e}")
        raise
