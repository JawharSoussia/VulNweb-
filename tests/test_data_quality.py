"""Data quality and freshness tests"""
import pytest
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class TestDataQuality:
    """Test data quality standards"""

    @pytest.fixture
    def processed_data(self):
        """Load processed training data"""
        df = pd.read_csv("data/train/train_processed.csv")
        return df

    def test_no_missing_values(self, processed_data):
        """No missing values in processed data"""
        assert processed_data.isnull().sum().sum() == 0, \
            f"Found {processed_data.isnull().sum().sum()} missing values"

    def test_no_duplicates(self, processed_data):
        """No excessive duplicate rows (high duplicates expected in network data)"""
        duplicate_count = processed_data.duplicated().sum()
        duplicate_ratio = duplicate_count / len(processed_data)

        # Network data naturally has duplicates after removing identifying columns (IPs, timestamps)
        # Accept up to 25% duplicates as this is expected behavior for network features
        assert duplicate_ratio < 0.25, \
            f"Excessive duplicates detected: {duplicate_ratio:.2%} ({duplicate_count} rows, threshold: 25%)"

    def test_numeric_columns_dtype(self, processed_data):
        """All columns are numeric (except target)"""
        for col in processed_data.columns:
            if col not in ['label', 'target', 'class']:
                assert processed_data[col].dtype in ['float64', 'int64'], \
                    f"Column {col} has non-numeric dtype: {processed_data[col].dtype}"

    def test_feature_bounds(self, processed_data):
        """Features within expected bounds (scaled features + clipped extremes)"""
        numeric_cols = processed_data.select_dtypes(include=['float64', 'int64']).columns

        for col in numeric_cols:
            # After RobustScaler + clipping, features should be in [-50, 50]
            max_val = processed_data[col].max()
            min_val = processed_data[col].min()

            assert max_val <= 50.1, \
                f"Column {col} exceeds maximum value: {max_val} (expected <= 50)"
            assert min_val >= -50.1, \
                f"Column {col} below minimum value: {min_val} (expected >= -50)"

    def test_target_distribution(self, processed_data):
        """Target variable has reasonable distribution"""
        target_col = 'label' if 'label' in processed_data.columns else processed_data.columns[-1]
        counts = processed_data[target_col].value_counts()

        # At least 2 classes
        assert len(counts) >= 2, "Target has less than 2 classes"

        # Check class imbalance ratio
        min_count = counts.min()
        max_count = counts.max()
        imbalance_ratio = min_count / max_count

        assert imbalance_ratio > 0.05, \
            f"Severe class imbalance detected: ratio={imbalance_ratio:.3f}"

    def test_feature_count_consistency(self):
        """Feature count consistent across splits"""
        train = pd.read_csv("data/train/train_processed.csv")
        val = pd.read_csv("data/train/val_processed.csv")
        test = pd.read_csv("data/test/test_processed.csv")

        assert train.shape[1] == val.shape[1] == test.shape[1], \
            f"Feature count mismatch: train={train.shape[1]}, " \
            f"val={val.shape[1]}, test={test.shape[1]}"

    def test_minimum_samples(self):
        """Datasets have minimum sample counts"""
        train = pd.read_csv("data/train/train_processed.csv")
        val = pd.read_csv("data/train/val_processed.csv")
        test = pd.read_csv("data/test/test_processed.csv")

        MIN_TRAIN_SAMPLES = 1000
        MIN_VAL_SAMPLES = 200
        MIN_TEST_SAMPLES = 200

        assert len(train) >= MIN_TRAIN_SAMPLES, \
            f"Train set too small: {len(train)} < {MIN_TRAIN_SAMPLES}"
        assert len(val) >= MIN_VAL_SAMPLES, \
            f"Val set too small: {len(val)} < {MIN_VAL_SAMPLES}"
        assert len(test) >= MIN_TEST_SAMPLES, \
            f"Test set too small: {len(test)} < {MIN_TEST_SAMPLES}"


class TestDataFreshness:
    """Test data freshness (if timestamp present)"""

    def test_recent_data(self):
        """Data is recent (within expected timeframe)"""
        # This assumes raw data has a timestamp column
        # Adjust based on your actual data
        raw_file = Path("data/raw")
        csv_files = list(raw_file.glob("*.csv"))

        if csv_files:
            file_stat = csv_files[0].stat()
            file_age_days = (datetime.now() - datetime.fromtimestamp(file_stat.st_mtime)).days

            # Data should be less than 90 days old
            assert file_age_days < 90, \
                f"Data is {file_age_days} days old - consider refreshing"