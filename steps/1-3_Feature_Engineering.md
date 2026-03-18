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

### Step 1: Create Feature Engineering Pipeline

**Create: `ml_model/training/feature_engineering.py`**

```python
"""Feature Engineering Pipeline"""
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.preprocessing import StandardScaler, RobustScaler, LabelEncoder
from sklearn.impute import SimpleImputer
from feature_engine.outliers import IQROutlier
from feature_engine.encoding import OrdinalEncoder
import logging
import pickle

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FeatureEngineer:
    """Feature engineering and preprocessing"""

    def __init__(self, train_df, val_df, test_df):
        """Initialize with train/val/test dataframes"""
        self.train = train_df.copy()
        self.val = val_df.copy()
        self.test = test_df.copy()
        self.preprocessor = {}

    def identify_columns(self, target_col='label'):
        """Identify numeric and categorical columns"""
        self.target_col = target_col
        self.numeric_cols = self.train.select_dtypes(
            include=['int64', 'float64']).columns.tolist()
        self.numeric_cols.remove(target_col) if target_col in self.numeric_cols else None

        self.categorical_cols = self.train.select_dtypes(
            include=['object']).columns.tolist()

        logger.info(f"Numeric columns: {len(self.numeric_cols)}")
        logger.info(f"Numeric: {self.numeric_cols[:5]}...")
        logger.info(f"Categorical columns: {len(self.categorical_cols)}")

    def handle_missing_values(self):
        """Handle missing values"""
        logger.info("\n" + "=" * 60)
        logger.info("HANDLING MISSING VALUES")
        logger.info("=" * 60)

        missing = self.train.isnull().sum()
        if missing.sum() == 0:
            logger.info("✓ No missing values in training set")
            return

        # Numeric: mean imputation
        numeric_imputer = SimpleImputer(strategy='mean')
        self.train[self.numeric_cols] = numeric_imputer.fit_transform(
            self.train[self.numeric_cols])
        self.val[self.numeric_cols] = numeric_imputer.transform(
            self.val[self.numeric_cols])
        self.test[self.numeric_cols] = numeric_imputer.transform(
            self.test[self.numeric_cols])

        self.preprocessor['numeric_imputer'] = numeric_imputer

        # Categorical: mode imputation
        for col in self.categorical_cols:
            mode_val = self.train[col].mode()[0]
            self.train[col].fillna(mode_val, inplace=True)
            self.val[col].fillna(mode_val, inplace=True)
            self.test[col].fillna(mode_val, inplace=True)

        logger.info("✓ Missing values handled")

    def handle_outliers(self):
        """Handle outliers using IQR method"""
        logger.info("\n" + "=" * 60)
        logger.info("HANDLING OUTLIERS (IQR Method)")
        logger.info("=" * 60)

        outlier_detector = IQROutlier(variables=self.numeric_cols)
        outlier_detector.fit(self.train)

        # Mark outliers (but don't remove - keep all data for training)
        outliers_train = outlier_detector.find_outliers(self.train)
        logger.info(f"Outliers in train set: {outliers_train.sum()} "
                   f"({outliers_train.sum()/len(self.train)*100:.2f}%)")

        # Cap outliers to upper/lower bounds instead of removing
        for col in self.numeric_cols:
            Q1 = self.train[col].quantile(0.25)
            Q3 = self.train[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            # Cap values
            self.train[col] = self.train[col].clip(lower_bound, upper_bound)
            self.val[col] = self.val[col].clip(lower_bound, upper_bound)
            self.test[col] = self.test[col].clip(lower_bound, upper_bound)

        logger.info("✓ Outliers capped to bounds")

    def encode_categorical(self):
        """Encode categorical variables"""
        logger.info("\n" + "=" * 60)
        logger.info("ENCODING CATEGORICAL VARIABLES")
        logger.info("=" * 60)

        if len(self.categorical_cols) == 0:
            logger.info("✓ No categorical columns to encode")
            return

        encoder = OrdinalEncoder(variables=self.categorical_cols)
        encoder.fit(self.train)

        self.train = encoder.transform(self.train)
        self.val = encoder.transform(self.val)
        self.test = encoder.transform(self.test)

        self.preprocessor['encoder'] = encoder
        logger.info(f"✓ Encoded {len(self.categorical_cols)} categorical columns")

    def create_derived_features(self):
        """Create derived features (domain-specific)"""
        logger.info("\n" + "=" * 60)
        logger.info("CREATING DERIVED FEATURES")
        logger.info("=" * 60)

        # Example: Create interaction features
        # Adjust based on your actual features

        for df in [self.train, self.val, self.test]:
            # Feature 1: Ratio features
            if 'bytes_in' in df.columns and 'bytes_out' in df.columns:
                df['bytes_ratio'] = (df['bytes_in'] + 1) / (df['bytes_out'] + 1)

            # Feature 2: Temporal patterns
            if 'duration' in df.columns:
                df['high_duration'] = (df['duration'] > df['duration'].median()).astype(int)

            # Feature 3: Connection density
            if 'packets_total' in df.columns and 'duration' in df.columns:
                df['packet_rate'] = df['packets_total'] / (df['duration'] + 1)

        logger.info("✓ Derived features created")

    def scale_features(self):
        """Scale numeric features"""
        logger.info("\n" + "=" * 60)
        logger.info("SCALING FEATURES")
        logger.info("=" * 60)

        # Use RobustScaler for data with outliers
        scaler = RobustScaler()
        self.train[self.numeric_cols] = scaler.fit_transform(
            self.train[self.numeric_cols])
        self.val[self.numeric_cols] = scaler.transform(self.val[self.numeric_cols])
        self.test[self.numeric_cols] = scaler.transform(
            self.test[self.numeric_cols])

        self.preprocessor['scaler'] = scaler
        logger.info(f"✓ Scaled {len(self.numeric_cols)} numeric features")

    def remove_low_variance_features(self, threshold=0.01):
        """Remove features with low variance"""
        logger.info("\n" + "=" * 60)
        logger.info("REMOVING LOW VARIANCE FEATURES")
        logger.info("=" * 60)

        variances = self.train[self.numeric_cols].var()
        low_var_features = variances[variances < threshold].index.tolist()

        if low_var_features:
            logger.warning(f"Removing {len(low_var_features)} low variance features:")
            for feat in low_var_features:
                logger.warning(f"  {feat}: variance = {variances[feat]:.6f}")

            self.train = self.train.drop(columns=low_var_features)
            self.val = self.val.drop(columns=low_var_features)
            self.test = self.test.drop(columns=low_var_features)

            # Update numeric_cols list
            self.numeric_cols = [c for c in self.numeric_cols
                                if c not in low_var_features]
        else:
            logger.info("✓ No low variance features to remove")

    def analyze_feature_importance(self):
        """Analyze feature importance post-engineering"""
        logger.info("\n" + "=" * 60)
        logger.info("FEATURE IMPORTANCE STATISTICS")
        logger.info("=" * 60)

        numeric_df = self.train[self.numeric_cols]
        importance = numeric_df.var().sort_values(ascending=False)

        logger.info("\nTop 10 Features by Variance:")
        for idx, (feat, var) in enumerate(importance.head(10).items(), 1):
            logger.info(f"  {idx}. {feat}: {var:.4f}")

        return importance

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
            "Feature count mismatch between sets!"

        # Check dtypes
        numeric_dtypes = [np.float64, np.int64]
        assert all(self.train.dtypes.isin(numeric_dtypes)), "Non-numeric data remains!"

        logger.info("✓ All validations passed")
        logger.info(f"Final feature count: {self.train.shape[1]}")

    def fit_and_transform(self):
        """Run complete pipeline"""
        logger.info("\n" + "=" * 60)
        logger.info("STARTING FEATURE ENGINEERING PIPELINE")
        logger.info("=" * 60)

        self.identify_columns()
        self.handle_missing_values()
        self.handle_outliers()
        self.encode_categorical()
        self.create_derived_features()
        self.scale_features()
        self.remove_low_variance_features()
        self.analyze_feature_importance()
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
    train_processed.to_csv("data/train/train_processed.csv", index=False)
    val_processed.to_csv("data/train/val_processed.csv", index=False)
    test_processed.to_csv("data/test/test_processed.csv", index=False)

    # Save preprocessor for later use
    with open("ml_model/training/preprocessor.pkl", 'wb') as f:
        pickle.dump(preprocessor, f)

    logger.info("\n✓ Processed data saved to data/train/ and data/test/")
    logger.info("✓ Preprocessor saved to ml_model/training/preprocessor.pkl")
```

---

### Step 2: Install Feature Engineering Package

```bash
# Install feature-engine for advanced preprocessing
pip install feature-engine

# Update requirements.txt
echo "feature-engine==1.6.0" >> requirements.txt
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

- [ ] Feature engineering script created
- [ ] Missing values handled
- [ ] Outliers identified and capped
- [ ] Categorical variables encoded
- [ ] Derived features created
- [ ] Features scaled using RobustScaler
- [ ] Low variance features removed
- [ ] Processed data saved
- [ ] Preprocessor object serialized
- [ ] Data validation passed
- [ ] Commit: `git add . && git commit -m "Add feature engineering pipeline"`

---

## 🔗 Next Steps

✅ **Task 1.3 Complete** → Move to **Task 1.4: Data Quality Tests (Data Contracts)**

---

**Created:** 2026-03-17
