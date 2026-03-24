"""Feature Engineering Pipeline for UNSW-NB15 Dataset"""
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.preprocessing import StandardScaler, RobustScaler, LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.feature_selection import VarianceThreshold
import logging
import pickle

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# UNSW-NB15 Features (remove non-numeric for engineering)
UNSW_CATEGORICAL = ['srcip', 'dstip', 'proto', 'state', 'service', 'attack']
UNSW_TARGET = 'label'

class FeatureEngineer:
    """Feature engineering and preprocessing for UNSW-NB15"""

    def __init__(self, train_df, val_df, test_df, target_col=UNSW_TARGET):
        """Initialize with train/val/test dataframes"""
        self.train = train_df.copy()
        self.val = val_df.copy()
        self.test = test_df.copy()
        self.target_col = target_col
        self.preprocessor = {}

    def identify_columns(self):
        """Identify numeric and categorical columns for UNSW-NB15"""
        logger.info("=" * 60)
        logger.info("IDENTIFYING FEATURES")
        logger.info("=" * 60)

        # Numeric features are all except categorical and target
        all_cols = set(self.train.columns)
        categorical = set(UNSW_CATEGORICAL) & all_cols
        target = {self.target_col} if self.target_col in all_cols else set()

        self.numeric_cols = list(all_cols - categorical - target)
        self.categorical_cols = list(categorical)

        logger.info(f"✓ Numeric columns ({len(self.numeric_cols)}): {self.numeric_cols[:5]}...")
        logger.info(f"✓ Categorical columns ({len(self.categorical_cols)}): {self.categorical_cols}")

    def drop_non_numeric_columns(self):
        """Remove non-numeric columns from dataframes"""
        logger.info("\n" + "=" * 60)
        logger.info("REMOVING NON-NUMERIC COLUMNS")
        logger.info("=" * 60)

        cols_to_keep = self.numeric_cols + [self.target_col]

        self.train = self.train[cols_to_keep]
        self.val = self.val[cols_to_keep]
        self.test = self.test[cols_to_keep]

        logger.info(f"✓ Reduced train shape to: {self.train.shape}")
        logger.info(f"✓ Reduced val shape to: {self.val.shape}")
        logger.info(f"✓ Reduced test shape to: {self.test.shape}")

    def handle_missing_values(self):
        """Handle missing values in numeric features"""
        logger.info("\n" + "=" * 60)
        logger.info("HANDLING MISSING VALUES")
        logger.info("=" * 60)

        # First, drop columns that are entirely empty
        cols_to_drop = []
        for col in self.numeric_cols:
            if self.train[col].isnull().all():
                cols_to_drop.append(col)
                logger.warning(f"Dropping completely empty column: {col}")

        if cols_to_drop:
            self.numeric_cols = [c for c in self.numeric_cols if c not in cols_to_drop]
            self.train = self.train.drop(columns=cols_to_drop)
            self.val = self.val.drop(columns=cols_to_drop)
            self.test = self.test.drop(columns=cols_to_drop)

        missing = self.train[self.numeric_cols].isnull().sum()
        if missing.sum() == 0:
            logger.info("✓ No missing values in training set")
            return

        logger.warning(f"Found {missing.sum()} missing values")

        # Use median for robustness (resistant to outliers)
        numeric_imputer = SimpleImputer(strategy='median')
        self.train[self.numeric_cols] = numeric_imputer.fit_transform(
            self.train[self.numeric_cols])
        self.val[self.numeric_cols] = numeric_imputer.transform(
            self.val[self.numeric_cols])
        self.test[self.numeric_cols] = numeric_imputer.transform(
            self.test[self.numeric_cols])

        self.preprocessor['numeric_imputer'] = numeric_imputer
        logger.info("✓ Missing values imputed with median")

    def handle_outliers(self):
        """Cap outliers at IQR bounds (don't remove to preserve attack patterns)"""
        logger.info("\n" + "=" * 60)
        logger.info("HANDLING OUTLIERS (IQR Method)")
        logger.info("=" * 60)

        for col in self.numeric_cols:
            Q1 = self.train[col].quantile(0.25)
            Q3 = self.train[col].quantile(0.75)
            IQR = Q3 - Q1

            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            # Count outliers
            outliers_train = ((self.train[col] < lower_bound) |
                             (self.train[col] > upper_bound)).sum()
            if outliers_train > 0:
                logger.debug(f"{col}: {outliers_train} outliers ({outliers_train/len(self.train)*100:.2f}%)")

            # Cap values
            self.train[col] = self.train[col].clip(lower_bound, upper_bound)
            self.val[col] = self.val[col].clip(lower_bound, upper_bound)
            self.test[col] = self.test[col].clip(lower_bound, upper_bound)

        logger.info("✓ Outliers capped to IQR bounds")

    def create_derived_features(self):
        """Create network-specific derived features from UNSW-NB15"""
        logger.info("\n" + "=" * 60)
        logger.info("CREATING DERIVED FEATURES (Network-specific)")
        logger.info("=" * 60)

        for df in [self.train, self.val, self.test]:
            # Bytes ratio
            if 'sbytes' in df.columns and 'dbytes' in df.columns:
                df['bytes_ratio'] = (df['sbytes'] + 1) / (df['dbytes'] + 1)

            # Packet ratio
            if 'spkts' in df.columns and 'dpkts' in df.columns:
                df['packet_ratio'] = (df['spkts'] + 1) / (df['dpkts'] + 1)

            # Bytes per packet (both directions)
            if 'sbytes' in df.columns and 'spkts' in df.columns:
                df['src_bytes_per_pkt'] = (df['sbytes'] + 1) / (df['spkts'] + 1)
            if 'dbytes' in df.columns and 'dpkts' in df.columns:
                df['dst_bytes_per_pkt'] = (df['dbytes'] + 1) / (df['dpkts'] + 1)

            # Connection duration patterns
            if 'dur' in df.columns:
                df['high_duration'] = (df['dur'] > df['dur'].median()).astype(int)
                df['log_duration'] = np.log1p(df['dur'])

            # TTL analysis
            if 'sttl' in df.columns and 'dttl' in df.columns:
                df['ttl_diff'] = np.abs(df['sttl'] - df['dttl'])

        # Update numeric_cols to include new features
        self.numeric_cols = [c for c in self.train.columns
                            if c != self.target_col]

        logger.info(f"✓ Created derived features. Total numeric: {len(self.numeric_cols)}")

    def scale_features(self):
        """Scale numeric features using RobustScaler"""
        logger.info("\n" + "=" * 60)
        logger.info("SCALING FEATURES (RobustScaler)")
        logger.info("=" * 60)

        # RobustScaler is resistant to outliers
        scaler = RobustScaler()
        self.train[self.numeric_cols] = scaler.fit_transform(
            self.train[self.numeric_cols])
        self.val[self.numeric_cols] = scaler.transform(self.val[self.numeric_cols])
        self.test[self.numeric_cols] = scaler.transform(
            self.test[self.numeric_cols])

        # Clip extreme values to [-50, 50] range
        for df in [self.train, self.val, self.test]:
            df[self.numeric_cols] = df[self.numeric_cols].clip(-50, 50)

        self.preprocessor['scaler'] = scaler
        logger.info(f"✓ Scaled {len(self.numeric_cols)} numeric features")
        logger.info("✓ Clipped extreme values to [-50, 50] range")

    def remove_low_variance_features(self, threshold=0.01):
        """Remove features with very low variance"""
        logger.info("\n" + "=" * 60)
        logger.info("REMOVING LOW VARIANCE FEATURES")
        logger.info("=" * 60)

        variance_selector = VarianceThreshold(threshold=threshold)
        variance_selector.fit(self.train[self.numeric_cols])

        support_mask = variance_selector.get_support()
        low_var_features = set(np.array(self.numeric_cols)[~support_mask])

        if low_var_features:
            logger.warning(f"Removing {len(low_var_features)} low variance features:")
            for feat in low_var_features:
                logger.warning(f"  {feat}")

            # Update numeric_cols first
            self.numeric_cols = list(np.array(self.numeric_cols)[support_mask])

            # Then transform all dataframes
            self.train = self.train[self.numeric_cols + [self.target_col]]
            self.val = self.val[self.numeric_cols + [self.target_col]]
            self.test = self.test[self.numeric_cols + [self.target_col]]
        else:
            logger.info("✓ No low variance features to remove")

        self.preprocessor['variance_selector'] = variance_selector

    def validate_output(self):
        """Validate preprocessed data"""
        logger.info("\n" + "=" * 60)
        logger.info("VALIDATING PREPROCESSED DATA")
        logger.info("=" * 60)

        # Check no missing values
        assert self.train.isnull().sum().sum() == 0, "Training data has missing values!"
        assert self.val.isnull().sum().sum() == 0, "Validation data has missing values!"
        assert self.test.isnull().sum().sum() == 0, "Test data has missing values!"

        # Check shapes
        assert self.train.shape[1] == self.val.shape[1] == self.test.shape[1], \
            "Feature count mismatch!"

        # Check dtypes
        assert all(pd.api.types.is_numeric_dtype(self.train[c])
                   for c in self.numeric_cols), "Non-numeric data remains!"

        logger.info("✓ All validations passed")
        logger.info(f"✓ Final shape: Train {self.train.shape} | Val {self.val.shape} | Test {self.test.shape}")

    def fit_and_transform(self):
        """Run complete feature engineering pipeline"""
        logger.info("\n" + "=" * 60)
        logger.info("STARTING UNSW-NB15 FEATURE ENGINEERING")
        logger.info("=" * 60)

        self.identify_columns()
        self.drop_non_numeric_columns()
        self.handle_missing_values()
        self.handle_outliers()
        self.create_derived_features()
        self.scale_features()
        self.remove_low_variance_features()
        self.validate_output()

        logger.info("\n" + "=" * 60)
        logger.info("✓ FEATURE ENGINEERING COMPLETE")
        logger.info("=" * 60)

        return self.train, self.val, self.test, self.preprocessor


if __name__ == "__main__":
    from pathlib import Path

    # Load data
    train_df = pd.read_csv("data/train/train.csv")
    val_df = pd.read_csv("data/val/val.csv")
    test_df = pd.read_csv("data/test/test.csv")

    # Create engineer
    engineer = FeatureEngineer(train_df, val_df, test_df)
    train_processed, val_processed, test_processed, preprocessor = engineer.fit_and_transform()

    # Save processed data
    output_dir = Path("data")
    train_processed.to_csv(output_dir / "train" / "train_processed.csv", index=False)
    val_processed.to_csv(output_dir / "train" / "val_processed.csv", index=False)
    test_processed.to_csv(output_dir / "test" / "test_processed.csv", index=False)

    # Save preprocessor
    with open("ml_model/training/preprocessor.pkl", 'wb') as f:
        pickle.dump(preprocessor, f)

    logger.info("\n✓ Processed data saved")
    logger.info("✓ Preprocessor saved to ml_model/training/preprocessor.pkl")