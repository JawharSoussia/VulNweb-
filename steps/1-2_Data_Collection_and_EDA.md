# Task 1.2: Data Collection & Exploratory Data Analysis (EDA)

**Phase:** Setup & Data Preparation
**Deadline:** Day 8
**Status:** ⏳ Pending
**Dependencies:** Task 1.1 complete

---

## 📋 Objective
Collect threat intelligence data, perform comprehensive EDA, analyze class distribution, and prepare dataset for feature engineering.

---

## 🎯 What to Do

### Step 1: Identify Data Sources

Choose 2-3 publicly available threat intelligence sources:

1. **CSICorp2012** - Flow-based intrusion detection dataset
   - Download: [http://www.unb.ca/cic/datasets/](http://www.unb.ca/cic/datasets/)
   - Format: CSV, ~5M records
   - Features: IP src/dst, port, protocol, bytes, packets, etc.

2. **UNSW-NB15** - Network intrusion dataset
   - Download: [https://www.unsw.adfa.edu.au/](https://www.unsw.adfa.edu.au/)
   - Format: CSV, ~250K records
   - Features: Network flow stats

3. **Kaggle Intrusion Detection**
   - Download: [https://www.kaggle.com/datasets/](kaggle.com)
   - Multiple curated datasets available

4. **VirusTotal API** (Optional - for simulated threats)
   - Download: [https://developers.virustotal.com/](https://developers.virustotal.com/)
   - Requires API key (free tier available)

**For this task:** Use a pre-curated dataset (~5,000-10,000 samples)

---

### Step 2: Create Data Directory & Download

```bash
# Create data directories
mkdir -p data/raw
mkdir -p data/processed
mkdir -p data/train
mkdir -p data/test

# If using UNSW-NB15 or similar, download and extract to data/raw/
# For this example, we'll create a synthetic dataset

cd data/raw
# Download UNSW-NB15 if available, or use provided CSV
wget https://example.com/dataset.csv  # Replace with actual source
cd ../../
```

---

### Step 3: Create Data Loading & EDA Script

**Create: `ml_model/training/eda.py`**

```python
"""Exploratory Data Analysis Script"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
DATA_RAW_PATH = Path("data/raw")
DATA_PROCESSED_PATH = Path("data/processed")
DATA_PROCESSED_PATH.mkdir(exist_ok=True)

class DataAnalyzer:
    """Perform comprehensive EDA on threat dataset"""

    def __init__(self, csv_path):
        """Initialize with CSV file path"""
        logger.info(f"Loading data from {csv_path}")
        self.df = pd.read_csv(csv_path)
        self.original_shape = self.df.shape

    def basic_info(self):
        """Display basic information"""
        logger.info("=" * 60)
        logger.info("BASIC INFORMATION")
        logger.info("=" * 60)
        logger.info(f"Dataset Shape: {self.df.shape}")
        logger.info(f"Memory Usage: {self.df.memory_usage(deep=True).sum() / 1e6:.2f} MB")
        logger.info(f"\nColumn Names & Types:\n{self.df.dtypes}")
        logger.info(f"\nMissing Values:\n{self.df.isnull().sum()}")
        logger.info(f"\nDuplicates: {self.df.duplicated().sum()}")

    def statistical_summary(self):
        """Display statistical summary"""
        logger.info("=" * 60)
        logger.info("STATISTICAL SUMMARY")
        logger.info("=" * 60)
        logger.info(f"\n{self.df.describe()}")

    def target_distribution(self):
        """Analyze target variable distribution"""
        logger.info("=" * 60)
        logger.info("TARGET VARIABLE DISTRIBUTION")
        logger.info("=" * 60)

        # Assuming target column is 'label' or 'target'
        # Adjust based on your dataset
        target_col = self._find_target_column()

        if target_col:
            value_counts = self.df[target_col].value_counts()
            logger.info(f"\n{target_col} Distribution:\n{value_counts}")

            percentages = (value_counts / len(self.df) * 100).round(2)
            logger.info(f"\nPercentages:\n{percentages}")

            # Plot
            plt.figure(figsize=(10, 6))
            value_counts.plot(kind='bar', color=['green', 'red'])
            plt.title(f'{target_col} Distribution')
            plt.xlabel(target_col)
            plt.ylabel('Count')
            plt.tight_layout()
            plt.savefig(f'{DATA_PROCESSED_PATH}/target_distribution.png')
            logger.info(f"✓ Saved: target_distribution.png")

            # Check class imbalance
            if len(value_counts) == 2:
                ratio = value_counts.min() / value_counts.max()
                logger.warning(f"⚠️  Class Imbalance Ratio: {ratio:.2f} (1 = balanced)")
                if ratio < 0.3:
                    logger.warning("⚠️  SEVERE IMBALANCE DETECTED - Will need SMOTE in Phase 2")

    def correlation_analysis(self):
        """Analyze feature correlations"""
        logger.info("=" * 60)
        logger.info("CORRELATION ANALYSIS")
        logger.info("=" * 60)

        # Get numeric columns only
        numeric_df = self.df.select_dtypes(include=[np.number])

        if len(numeric_df.columns) > 1:
            corr_matrix = numeric_df.corr()

            # Plot correlation heatmap
            plt.figure(figsize=(12, 10))
            sns.heatmap(corr_matrix, cmap='coolwarm', center=0,
                       square=True, annot=False)
            plt.title('Feature Correlation Matrix')
            plt.tight_layout()
            plt.savefig(f'{DATA_PROCESSED_PATH}/correlation_matrix.png')
            logger.info(f"✓ Saved: correlation_matrix.png")

            # Find highly correlated features
            logger.info("\nHighly Correlated Features (> 0.8):")
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    if abs(corr_matrix.iloc[i, j]) > 0.8:
                        col1, col2 = corr_matrix.columns[i], corr_matrix.columns[j]
                        corr_val = corr_matrix.iloc[i, j]
                        logger.info(f"  {col1} <-> {col2}: {corr_val:.3f}")

    def missing_data_analysis(self):
        """Analyze missing data patterns"""
        logger.info("=" * 60)
        logger.info("MISSING DATA ANALYSIS")
        logger.info("=" * 60)

        missing = self.df.isnull().sum()
        missing_pct = (missing / len(self.df) * 100).round(2)

        if missing.sum() > 0:
            logger.warning("Missing values detected:")
            for col, count, pct in zip(missing.index, missing.values, missing_pct.values):
                if count > 0:
                    logger.warning(f"  {col}: {count} ({pct}%)")
        else:
            logger.info("✓ No missing values detected")

    def outlier_detection(self):
        """Detect outliers using IQR method"""
        logger.info("=" * 60)
        logger.info("OUTLIER DETECTION (IQR Method)")
        logger.info("=" * 60)

        numeric_df = self.df.select_dtypes(include=[np.number])

        outlier_counts = {}
        for col in numeric_df.columns:
            Q1 = numeric_df[col].quantile(0.25)
            Q3 = numeric_df[col].quantile(0.75)
            IQR = Q3 - Q1

            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            outliers = ((numeric_df[col] < lower_bound) |
                       (numeric_df[col] > upper_bound)).sum()
            outlier_counts[col] = outliers

        # Display columns with outliers
        outlier_cols = {k: v for k, v in outlier_counts.items() if v > 0}
        if outlier_cols:
            logger.warning("Columns with outliers:")
            for col, count in sorted(outlier_cols.items(),
                                    key=lambda x: x[1], reverse=True)[:10]:
                pct = (count / len(self.df) * 100)
                logger.warning(f"  {col}: {count} ({pct:.2f}%)")
        else:
            logger.info("✓ No significant outliers detected")

    def feature_distributions(self, top_n=5):
        """Visualize top N feature distributions"""
        logger.info("=" * 60)
        logger.info(f"TOP {top_n} FEATURE DISTRIBUTIONS")
        logger.info("=" * 60)

        numeric_df = self.df.select_dtypes(include=[np.number])

        # Select top features by variance
        top_features = numeric_df.var().nlargest(top_n).index

        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        axes = axes.flatten()

        for idx, feature in enumerate(top_features):
            axes[idx].hist(numeric_df[feature], bins=50, edgecolor='black', alpha=0.7)
            axes[idx].set_title(f'Distribution of {feature}')
            axes[idx].set_xlabel(feature)
            axes[idx].set_ylabel('Frequency')

        plt.tight_layout()
        plt.savefig(f'{DATA_PROCESSED_PATH}/feature_distributions.png')
        logger.info(f"✓ Saved: feature_distributions.png")

    def _find_target_column(self):
        """Automatically find target column"""
        possible_names = ['label', 'target', 'class', 'threat', 'attack',
                         'intrusion', 'malicious', 'benign']
        for col in self.df.columns:
            if any(name in col.lower() for name in possible_names):
                return col
        # Default to last column if not found
        logger.warning(f"⚠️  Target column not found; using last column: {self.df.columns[-1]}")
        return self.df.columns[-1]

    def generate_report(self):
        """Generate complete EDA report"""
        logger.info("\n" + "=" * 60)
        logger.info("STARTING COMPREHENSIVE EDA")
        logger.info("=" * 60)

        self.basic_info()
        self.missing_data_analysis()
        self.statistical_summary()
        self.target_distribution()
        self.correlation_analysis()
        self.outlier_detection()
        self.feature_distributions()

        logger.info("\n" + "=" * 60)
        logger.info("✓ EDA COMPLETE")
        logger.info("=" * 60)
        logger.info(f"Generated files in: {DATA_PROCESSED_PATH}/")


if __name__ == "__main__":
    # Find dataset
    csv_files = list(DATA_RAW_PATH.glob("*.csv"))

    if not csv_files:
        logger.error("❌ No CSV files found in data/raw/")
        logger.info("Please download a dataset to data/raw/")
        exit(1)

    # Use first CSV found
    csv_path = csv_files[0]
    logger.info(f"Using dataset: {csv_path}")

    # Run analysis
    analyzer = DataAnalyzer(csv_path)
    analyzer.generate_report()
```

---

### Step 4: Run EDA

```bash
# Navigate to project root
cd /path/to/projet\ 2

# Activate virtual environment
source venv/bin/activate

# Download a sample dataset (UNSW-NB15)
# Or create synthetic data for testing

# Run EDA
python ml_model/training/eda.py
```

---

### Step 5: Generate EDA Report

```bash
# Create EDA summary report
mkdir -p docs/eda_reports

# The script will generate:
# data/processed/target_distribution.png
# data/processed/correlation_matrix.png
# data/processed/feature_distributions.png
# data/processed/outlier_summary.txt (from script output)
```

---

### Step 6: Create Data Splitting Script

**Create: `ml_model/training/split_data.py`**

```python
"""Split data into train/test/validation sets"""
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def split_dataset(csv_path, test_size=0.2, val_size=0.1, random_state=42):
    """
    Split dataset into train/val/test sets

    Args:
        csv_path: Path to CSV file
        test_size: Proportion for test set (0.2 = 20%)
        val_size: Proportion for validation from remaining (0.1 = 10% of 80%)
        random_state: For reproducibility
    """

    logger.info(f"Loading data from {csv_path}")
    df = pd.read_csv(csv_path)
    logger.info(f"Total samples: {len(df)}")

    # Find target column
    target_col = None
    for col in df.columns:
        if any(name in col.lower() for name in ['label', 'target', 'class']):
            target_col = col
            break

    if not target_col:
        target_col = df.columns[-1]

    logger.info(f"Target column: {target_col}")

    # Stratified split to maintain class distribution
    # Train + Val vs Test
    train_val, test = train_test_split(
        df,
        test_size=test_size,
        stratify=df[target_col],
        random_state=random_state
    )

    # Further split train into train and val
    actual_val_size = val_size / (1 - test_size)
    train, val = train_test_split(
        train_val,
        test_size=actual_val_size,
        stratify=train_val[target_col],
        random_state=random_state
    )

    # Save splits
    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)

    train.to_csv(output_dir / "train" / "train.csv", index=False)
    val.to_csv(output_dir / "train" / "val.csv", index=False)
    test.to_csv(output_dir / "test" / "test.csv", index=False)

    logger.info(f"✓ Train set: {len(train)} samples ({len(train)/len(df)*100:.1f}%)")
    logger.info(f"✓ Val set:   {len(val)} samples ({len(val)/len(df)*100:.1f}%)")
    logger.info(f"✓ Test set:  {len(test)} samples ({len(test)/len(df)*100:.1f}%)")

    # Check class distribution
    logger.info("\nClass Distribution in Train:")
    logger.info(train[target_col].value_counts())

    return train, val, test

if __name__ == "__main__":
    csv_files = list(Path("data/raw").glob("*.csv"))
    if csv_files:
        split_dataset(csv_files[0])
```

---

### Step 7: Document Findings

**Create: `docs/eda_reports/EDA_Summary.md`**

```markdown
# EDA Summary Report

**Date:** 2026-03-17
**Dataset:** [Dataset Name]

## Key Findings

### Dataset Overview
- Total Samples: [X]
- Features: [Y]
- Target Variable: [Z]
- Missing Values: [%]

### Class Distribution
- Class 0 (Safe): [X] samples ([%])
- Class 1 (Threat): [Y] samples ([%])
- **Imbalance Ratio:** [ratio] (⚠️  if < 0.3)

### Top 10 Important Features (by variance)
1. [Feature 1]
2. [Feature 2]
...

### Anomalies Detected
- [Outliers in feature X: Y%]
- [Missing values in feature Z: A%]

### Next Steps (Phase 1.3)
- Apply feature engineering to [features]
- Use SMOTE for class imbalance (if ratio < 0.3)
- Handle outliers using [method]
```

---

## 📊 Expected Outputs

```
data/
├── raw/
│   └── dataset.csv (downloaded)
├── processed/
│   ├── target_distribution.png
│   ├── correlation_matrix.png
│   └── feature_distributions.png
├── train/
│   ├── train.csv
│   └── val.csv
└── test/
    └── test.csv

docs/eda_reports/
└── EDA_Summary.md
```

---

## ✅ Checklist

- [ ] Dataset downloaded to `data/raw/`
- [ ] `eda.py` script created and tested
- [ ] EDA report generated with visualizations
- [ ] Data split into train/val/test
- [ ] Class distribution analyzed
- [ ] Missing values identified
- [ ] Outliers detected
- [ ] EDA summary documented
- [ ] Commit to git: `git add . && git commit -m "Add data EDA and splitting"`

---

## 🔗 Next Steps

✅ **Task 1.2 Complete** → Move to **Task 1.3: Feature Engineering**

---

**Created:** 2026-03-17
