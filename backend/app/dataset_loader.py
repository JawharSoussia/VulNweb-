"""UNSW-NB15 Dataset Loading and Preprocessing"""
import pandas as pd
import numpy as np
import os
import logging
from pathlib import Path
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

# UNSW-NB15 Feature columns
UNSW_FEATURES = [
    'srcip', 'sport', 'dstip', 'dstp', 'proto', 'state', 'dur', 'sbytes', 'dbytes',
    'sttl', 'dttl', 'sloss', 'dloss', 'service', 'sload', 'dload', 'spkts', 'dpkts',
    'swin', 'dwin', 'stcpb', 'dtcpb', 'smeansz', 'dmeansz', 'sjitx', 'djitx', 'stime',
    'ltime', 'sintpkt', 'dintpkt', 'tcprtt', 'synack', 'ackdat', 'is_sm_ips_ports',
    'ct_state_ttl', 'ct_flw_http_mthd', 'is_ftp_login', 'ct_ftp_cmd', 'ct_srv_src',
    'ct_srv_dst', 'ct_dst_ltm', 'ct_src_ltm', 'ct_src_dport_ltm', 'ct_dst_sport_ltm',
    'ct_dst_src_ltm', 'attack_cat', 'Label'
]

class UNSWDatasetLoader:
    """Loader for UNSW-NB15 dataset"""

    def __init__(self, data_dir: str = "./data"):
        self.data_dir = Path(data_dir)
        # Create directory if it doesn't exist (only at root level)
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Dataset loader initialized with data_dir: {self.data_dir}")
        except Exception as e:
            logger.warning(f"Could not create data directory {self.data_dir}: {e}")
            # Continue anyway - directory might already exist

    def download_kaggle_dataset(self) -> bool:
        """
        Download UNSW-NB15 dataset from Kaggle

        Requires kaggle API credentials configured in ~/.kaggle/kaggle.json

        Returns:
            True if successful, False otherwise
        """
        try:
            from kaggle.api.kaggle_api_extended import KaggleApi

            api = KaggleApi()
            api.authenticate()

            dataset_name = "mrwellsdavid/unsw-nb15"
            logger.info(f"Downloading {dataset_name} from Kaggle...")

            api.dataset_download_files(dataset_name, path=self.data_dir, unzip=True)
            logger.info(f"Dataset downloaded to {self.data_dir}")
            return True

        except Exception as e:
            logger.error(f"Error downloading dataset: {str(e)}")
            return False

    def load_dataset(self, filename: str = "UNSW_NB15_training-set.csv") -> Optional[pd.DataFrame]:
        """
        Load UNSW-NB15 CSV file

        Args:
            filename: Name of the CSV file to load

        Returns:
            DataFrame with the dataset, or None if file not found
        """
        file_path = self.data_dir / filename

        if not file_path.exists():
            logger.error(f"Dataset file not found: {file_path}")
            return None

        try:
            df = pd.read_csv(file_path)
            logger.info(f"Loaded dataset with shape {df.shape}")
            return df

        except Exception as e:
            logger.error(f"Error loading dataset: {str(e)}")
            return None

    @staticmethod
    def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess UNSW-NB15 data

        Handles:
        - Missing values
        - Categorical encoding
        - Feature scaling

        Args:
            df: Raw dataset

        Returns:
            Preprocessed dataset
        """
        df = df.copy()

        # Handle missing values
        df = df.fillna(df.mean(numeric_only=True))

        # Encode categorical variables
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            if col != 'Label' and col != 'attack_cat':
                df[col] = pd.factorize(df[col])[0]

        # Encode target variable
        if 'Label' in df.columns:
            df['Label'] = (df['Label'] == 1).astype(int)

        logger.info(f"Preprocessed data shape: {df.shape}")
        return df

    @staticmethod
    def extract_features(df: pd.DataFrame, exclude_cols: list = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Extract features and labels for ML model

        Args:
            df: Preprocessed dataset
            exclude_cols: Columns to exclude from features

        Returns:
            Tuple of (X, y) for ML model training
        """
        if exclude_cols is None:
            exclude_cols = ['Label', 'attack_cat']

        X = df.drop(columns=exclude_cols, errors='ignore')
        y = df['Label'] if 'Label' in df.columns else None

        logger.info(f"Feature matrix shape: {X.shape}, Target shape: {y.shape if y is not None else 'N/A'}")
        return X.values, y.values if y is not None else None

    def get_attack_categories(self, df: pd.DataFrame) -> dict:
        """
        Get distribution of attack categories

        Args:
            df: Dataset with attack_cat column

        Returns:
            Dictionary with attack category counts
        """
        if 'attack_cat' not in df.columns:
            logger.warning("attack_cat column not found")
            return {}

        return df['attack_cat'].value_counts().to_dict()

    def split_benign_malicious(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Split dataset into benign and malicious samples

        Args:
            df: Dataset with Label column

        Returns:
            Tuple of (benign_df, malicious_df)
        """
        if 'Label' not in df.columns:
            logger.error("Label column not found")
            return df, pd.DataFrame()

        benign = df[df['Label'] == 0]
        malicious = df[df['Label'] == 1]

        logger.info(f"Benign samples: {len(benign)}, Malicious samples: {len(malicious)}")
        return benign, malicious
