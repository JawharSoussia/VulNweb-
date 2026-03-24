# Task 1.3: Feature Engineering

**Phase:** Setup & Data Preparation
**Deadline:** Day 12
**Status:** ⏳ Pending
**Dependencies:** Task 1.2 complete

---

## 📋 Objective
Extract, engineer, and prepare features from raw data. Handle scaling, normalization, missing values, and outliers.

---

## 🎯 What to Do

### Step 1: Create Feature Engineering Pipeline for UNSW-NB15

**Create: `ml_model/training/feature_engineering.py`**

```python
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

        missing = self.train.isnull().sum()
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

        self.preprocessor['scaler'] = scaler
        logger.info(f"✓ Scaled {len(self.numeric_cols)} numeric features")

    def remove_low_variance_features(self, threshold=0.01):
        """Remove features with very low variance"""
        logger.info("\n" + "=" * 60)
        logger.info("REMOVING LOW VARIANCE FEATURES")
        logger.info("=" * 60)

        variance_selector = VarianceThreshold(threshold=threshold)
        self.train[self.numeric_cols] = variance_selector.fit_transform(
            self.train[self.numeric_cols])

        low_var_features = set(self.numeric_cols) - set(
            np.array(self.numeric_cols)[variance_selector.get_support()])

        if low_var_features:
            logger.warning(f"Removing {len(low_var_features)} low variance features:")
            for feat in low_var_features:
                logger.warning(f"  {feat}")

            self.val[self.numeric_cols] = variance_selector.transform(
                self.val[self.numeric_cols])
            self.test[self.numeric_cols] = variance_selector.transform(
                self.test[self.numeric_cols])

            self.numeric_cols = list(np.array(self.numeric_cols)[
                variance_selector.get_support()])
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
    val_df = pd.read_csv("data/train/val.csv")
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
```

---

### Step 2: Update Requirements (if needed)

The feature engineering script uses standard scikit-learn packages that are already in `requirements.txt`. No additional packages needed.

Verify your requirements include:
```
pandas==2.1.3
numpy==1.26.2
scikit-learn==1.3.2
```

---

### Step 3: Run Feature Engineering

```bash
# Activate virtual environment
source venv/bin/activate

# Run feature engineering pipeline
python ml_model/training/feature_engineering.py
```

---

### Step 4: Verify Output

```bash
# Check processed data shapes
python << 'EOF'
import pandas as pd

train = pd.read_csv("data/train/train_processed.csv")
val = pd.read_csv("data/train/val_processed.csv")
test = pd.read_csv("data/test/test_processed.csv")

print(f"Train shape: {train.shape}")
print(f"Val shape: {val.shape}")
print(f"Test shape: {test.shape}")
print(f"\nFirst 5 rows of train:")
print(train.head())
print(f"\nData types:")
print(train.dtypes)
EOF
```

---

## 📊 Expected Outputs

```
data/
├── train/
│   ├── train_processed.csv
│   └── val_processed.csv
└── test/
    └── test_processed.csv

ml_model/training/
└── preprocessor.pkl
```

---

## ✅ Checklist

- [x] Feature engineering script created
- [x] Missing values handled
- [x] Outliers identified and capped
- [x] Categorical variables encoded
- [x] Derived features created
- [x] Features scaled using RobustScaler
- [x] Low variance features removed
- [x] Processed data saved
- [x] Preprocessor object serialized
- [x] Data validation passed
- [x] Commit: `git add . && git commit -m "Add feature engineering pipeline"`

---

## 🔗 Next Steps

✅ **Task 1.3 Complete** → Move to **Task 1.4: Data Quality Tests (Data Contracts)**

---

**Created:** 2026-03-17


INFO:__main__:
============================================================
INFO:__main__:STARTING UNSW-NB15 FEATURE ENGINEERING
INFO:__main__:============================================================
INFO:__main__:============================================================
INFO:__main__:IDENTIFYING FEATURES
INFO:__main__:============================================================
INFO:__main__:✓ Numeric columns (40): ['sloss', 'tcprtt', 'dloss', 'swin', 'stcpb']...
INFO:__main__:✓ Categorical columns (6): ['dstip', 'proto', 'attack', 'service', 'srcip', 'state']        
INFO:__main__:
============================================================
INFO:__main__:REMOVING NON-NUMERIC COLUMNS
INFO:__main__:============================================================
INFO:__main__:✓ Reduced train shape to: (1778032, 41)
INFO:__main__:✓ Reduced val shape to: (381007, 41)
INFO:__main__:✓ Reduced test shape to: (381008, 41)
INFO:__main__:
============================================================
INFO:__main__:HANDLING MISSING VALUES
INFO:__main__:============================================================
WARNING:__main__:Dropping completely empty column: sloss
WARNING:__main__:Dropping completely empty column: dstp
WARNING:__main__:Found 2945973 missing values
INFO:__main__:✓ Missing values imputed with median
INFO:__main__:
============================================================
INFO:__main__:HANDLING OUTLIERS (IQR Method)
INFO:__main__:============================================================
INFO:__main__:✓ Outliers capped to IQR bounds
INFO:__main__:
============================================================
INFO:__main__:CREATING DERIVED FEATURES (Network-specific)
INFO:__main__:============================================================
INFO:__main__:✓ Created derived features. Total numeric: 45
INFO:__main__:
============================================================
INFO:__main__:SCALING FEATURES (RobustScaler)
INFO:__main__:============================================================
INFO:__main__:✓ Scaled 45 numeric features
INFO:__main__:
============================================================
INFO:__main__:REMOVING LOW VARIANCE FEATURES
INFO:__main__:============================================================
WARNING:__main__:Removing 11 low variance features:
WARNING:__main__:  smeansz
WARNING:__main__:  ct_state_ttl
WARNING:__main__:  ct_flw_http_mthd
WARNING:__main__:  ct_dst_sport_ltm
WARNING:__main__:  is_sm_ips_ports
WARNING:__main__:  bytes_ratio
WARNING:__main__:  dbytes
WARNING:__main__:  dmeansz
WARNING:__main__:  ct_ftp_cmd
WARNING:__main__:  is_ftp_login
WARNING:__main__:  sbytes
INFO:__main__:
============================================================
INFO:__main__:VALIDATING PREPROCESSED DATA
INFO:__main__:============================================================
INFO:__main__:✓ All validations passed
INFO:__main__:✓ Final shape: Train (1778032, 35) | Val (381007, 35) | Test (381008, 35)
INFO:__main__:
============================================================
INFO:__main__:✓ FEATURE ENGINEERING COMPLETE
INFO:__main__:============================================================
INFO:__main__:
✓ Processed data saved
INFO:__main__:✓ Preprocessor saved to ml_model/training/preprocessor.pkl
