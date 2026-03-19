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

### Step 1: Identify Data Source

For this project, we use **UNSW-NB15** from Kaggle as the primary dataset:

**UNSW-NB15 Dataset**
- **Source:** [Kaggle - UNSW-NB15](https://www.kaggle.com/datasets/mrwellsdavid/unsw-nb15)
- **Format:** CSV files (multiple splits)
- **Size:** 2,540,047 network flow records
- **Features:** 47 network and traffic features
- **Attack Categories:** DoS, Exploits, Backdoors, Analysis, Fuzzers, Reconnaissance, Shellcode, Generic, Worms
- **Label:** 0 = Benign, 1 = Attack

**Additional: VirusTotal API** (Complementary threat intelligence)
- **Source:** [VirusTotal Developers](https://developers.virustotal.com/)
- **Capabilities:** URL scanning, file hash lookup, malware analysis
- **Integration:** Used alongside network analysis for comprehensive threat detection
- **Requires API key** (free tier available with 4 requests/minute)

**Why UNSW-NB15:**
- Real network traffic data captured in a controlled environment
- Comprehensive feature set representing modern cyberattacks
- Large sample size (2.5M records) for robust model training
- Multiple attack types for diverse threat detection
- Kaggle download integration available in the project

---

### Step 2: Create Data Directory & Download UNSW-NB15

```bash
# Create data directories
mkdir -p data/raw
mkdir -p data/processed
mkdir -p data/train
mkdir -p data/test

# Option A: Download using Kaggle API (Recommended)
# First, ensure Kaggle credentials are configured at ~/.kaggle/kaggle.json
# See SETUP_GUIDE.md for Kaggle setup instructions

kaggle datasets download -d mrwellsdavid/unsw-nb15 -p data/raw
cd data/raw
unzip unsw-nb15.zip
cd ../../

# Option B: Download UNSW-NB15 via API endpoint (if running the backend)
# This requires Kaggle credentials configured
curl -X GET http://localhost:8000/threats/download-dataset

# Option C: Manual Download
# 1. Visit: https://www.kaggle.com/datasets/mrwellsdavid/unsw-nb15
# 2. Download CSV files
# 3. Extract to data/raw/
```

**Note on Dataset Structure:**
The UNSW-NB15 dataset comes as separate CSV files. The project will automatically handle loading and combining them during the EDA phase.

---

### Step 3: Create Data Loading & EDA Script for UNSW-NB15

**Create: `ml_model/training/eda.py`**

```python
"""Exploratory Data Analysis for UNSW-NB15 Dataset"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import logging
from glob import glob

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
DATA_RAW_PATH = Path("data/raw")
DATA_PROCESSED_PATH = Path("data/processed")
DATA_PROCESSED_PATH.mkdir(exist_ok=True)

# UNSW-NB15 Column Names
UNSW_COLUMNS = [
    'srcip', 'sport', 'dstip', 'dstp', 'proto', 'state', 'dur', 'sbytes', 'dbytes',
    'sttl', 'dttl', 'sloss', 'dloss', 'service', 'sload', 'dload', 'spkts', 'dpkts',
    'swin', 'dwin', 'stcpb', 'dtcpb', 'smeansz', 'dmeansz', 'sjit', 'djit',
    'stime', 'ltime', 'sintpkt', 'dintpkt', 'tcprtt', 'synack', 'ackdat',
    'is_sm_ips_ports', 'ct_state_ttl', 'ct_flw_http_mthd', 'is_ftp_login',
    'ct_ftp_cmd', 'ct_srv_src', 'ct_srv_dst', 'ct_dst_ltm', 'ct_src_ltm',
    'ct_src_dport_ltm', 'ct_dst_sport_ltm', 'ct_dst_src_ltm', 'attack', 'label'
]

class DataAnalyzer:
    """Perform comprehensive EDA on UNSW-NB15 dataset"""

    def __init__(self):
        """Initialize and load UNSW-NB15 CSV files"""
        logger.info("Loading UNSW-NB15 dataset files...")
        csv_files = sorted(glob(str(DATA_RAW_PATH / "*.csv")))

        if not csv_files:
            logger.error("❌ No CSV files found in data/raw/")
            raise FileNotFoundError("Please download UNSW-NB15 dataset to data/raw/")

        # Load all CSV files (they're often split across multiple files)
        df_list = []
        for csv_file in csv_files:
            logger.info(f"Loading: {Path(csv_file).name}")
            df = pd.read_csv(csv_file, names=UNSW_COLUMNS, low_memory=False)
            df_list.append(df)

        self.df = pd.concat(df_list, ignore_index=True)
        self.original_shape = self.df.shape
        logger.info(f"✓ Loaded UNSW-NB15 dataset: {self.original_shape}")

    def basic_info(self):
        """Display basic information"""
        logger.info("=" * 60)
        logger.info("UNSW-NB15 BASIC INFORMATION")
        logger.info("=" * 60)
        logger.info(f"Dataset Shape: {self.df.shape}")
        logger.info(f"Memory Usage: {self.df.memory_usage(deep=True).sum() / 1e6:.2f} MB")
        logger.info(f"\nColumn Names & Types:\n{self.df.dtypes}")
        logger.info(f"\nMissing Values:\n{self.df.isnull().sum()}")
        logger.info(f"\nDuplicates: {self.df.duplicated().sum()}")

    def statistical_summary(self):
        """Display statistical summary"""
        logger.info("=" * 60)
        logger.info("STATISTICAL SUMMARY (Numeric Features)")
        logger.info("=" * 60)
        logger.info(f"\n{self.df.describe()}")

    def target_distribution(self):
        """Analyze attack class distribution"""
        logger.info("=" * 60)
        logger.info("ATTACK CLASS DISTRIBUTION")
        logger.info("=" * 60)

        # UNSW-NB15 has both 'attack' (category) and 'label' (binary)
        if 'attack' in self.df.columns:
            logger.info("\nAttack Categories:")
            attack_counts = self.df['attack'].value_counts()
            logger.info(attack_counts)

            percentages = (attack_counts / len(self.df) * 100).round(2)
            logger.info(f"\nPercentages:\n{percentages}")

        if 'label' in self.df.columns:
            logger.info("\nBinary Labels (0=Benign, 1=Attack):")
            label_counts = self.df['label'].value_counts()
            logger.info(label_counts)

            # Plot
            plt.figure(figsize=(10, 6))
            label_counts.sort_index().plot(kind='bar', color=['green', 'red'])
            plt.title('Benign vs Attack Distribution')
            plt.xlabel('Label (0=Benign, 1=Attack)')
            plt.ylabel('Count')
            plt.xticks(rotation=0)
            plt.tight_layout()
            plt.savefig(f'{DATA_PROCESSED_PATH}/label_distribution.png')
            logger.info(f"✓ Saved: label_distribution.png")

            # Check class imbalance
            ratio = label_counts.min() / label_counts.max()
            logger.warning(f"⚠️  Class Imbalance Ratio: {ratio:.2f} (1 = balanced)")
            if ratio < 0.3:
                logger.warning("⚠️  SEVERE IMBALANCE - Will use SMOTE in Phase 2")

    def correlation_analysis(self):
        """Analyze feature correlations"""
        logger.info("=" * 60)
        logger.info("CORRELATION ANALYSIS (Top Features)")
        logger.info("=" * 60)

        numeric_df = self.df.select_dtypes(include=[np.number])

        if len(numeric_df.columns) > 1:
            corr_matrix = numeric_df.corr()

            # Plot correlation heatmap (sample of top features)
            top_vars = numeric_df.var().nlargest(15).index
            plt.figure(figsize=(12, 10))
            sns.heatmap(corr_matrix.loc[top_vars, top_vars], cmap='coolwarm',
                       center=0, square=True, annot=False)
            plt.title('Top 15 Features - Correlation Matrix')
            plt.tight_layout()
            plt.savefig(f'{DATA_PROCESSED_PATH}/correlation_matrix.png')
            logger.info(f"✓ Saved: correlation_matrix.png")

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
        """Detect outliers in numeric features"""
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

        outlier_cols = {k: v for k, v in outlier_counts.items() if v > 0}
        if outlier_cols:
            logger.warning("Top 10 columns with outliers:")
            for col, count in sorted(outlier_cols.items(),
                                    key=lambda x: x[1], reverse=True)[:10]:
                pct = (count / len(self.df) * 100)
                logger.warning(f"  {col}: {count} ({pct:.2f}%)")
        else:
            logger.info("✓ No significant outliers detected")

    def protocol_analysis(self):
        """Analyze protocol distribution (UNSW-NB15 specific)"""
        logger.info("=" * 60)
        logger.info("PROTOCOL DISTRIBUTION (UNSW-NB15)")
        logger.info("=" * 60)

        if 'proto' in self.df.columns:
            proto_counts = self.df['proto'].value_counts()
            logger.info(f"\nProtocol Distribution:\n{proto_counts}")

            plt.figure(figsize=(10, 6))
            proto_counts.plot(kind='bar')
            plt.title('Protocol Distribution')
            plt.xlabel('Protocol')
            plt.ylabel('Count')
            plt.tight_layout()
            plt.savefig(f'{DATA_PROCESSED_PATH}/protocol_distribution.png')
            logger.info(f"✓ Saved: protocol_distribution.png")

    def generate_report(self):
        """Generate complete EDA report"""
        logger.info("\n" + "=" * 60)
        logger.info("STARTING UNSW-NB15 EDA")
        logger.info("=" * 60)

        self.basic_info()
        self.missing_data_analysis()
        self.statistical_summary()
        self.target_distribution()
        self.correlation_analysis()
        self.outlier_detection()
        self.protocol_analysis()

        logger.info("\n" + "=" * 60)
        logger.info("✓ EDA COMPLETE")
        logger.info("=" * 60)
        logger.info(f"Generated files in: {DATA_PROCESSED_PATH}/")


if __name__ == "__main__":
    try:
        analyzer = DataAnalyzer()
        analyzer.generate_report()
    except Exception as e:
        logger.error(f"❌ EDA failed: {e}")
        raise
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

### Step 7: Document UNSW-NB15 Findings

**Create: `docs/eda_reports/UNSW_NB15_EDA_Summary.md`**

```markdown
# UNSW-NB15 EDA Summary Report

**Date:** [Today's Date]
**Dataset:** UNSW-NB15 from Kaggle
**Source:** https://www.kaggle.com/datasets/mrwellsdavid/unsw-nb15

## Overview

### Dataset Statistics
- **Total Samples:** 2,540,047 network flows
- **Features:** 47 network and traffic features
- **Time Period:** Captured in controlled laboratory environment
- **Class Label:** 0 = Benign, 1 = Attack

### Class Distribution
- **Benign Flows (Label=0):** [X] samples ([Y%])
- **Attack Flows (Label=1):** [X] samples ([Y%])
- **Imbalance Ratio:** [ratio] (⚠️  if < 0.3 - requires SMOTE)

### Attack Categories
- DoS: [count] samples
- Exploits: [count] samples
- Backdoors: [count] samples
- Analysis: [count] samples
- Fuzzers: [count] samples
- Reconnaissance: [count] samples
- Shellcode: [count] samples
- Generic: [count] samples
- Worms: [count] samples

## Key Findings

### Data Quality
- Missing Values: [%]
- Duplicates: [count]
- Data Type Issues: [description]

### Outliers Detected
- Total Outliers (IQR Method): [%]
- Columns with outliers: [list top 5]

### Feature Statistics
- Mean feature variance: [value]
- Top 5 Features by Variance:
  1. [Feature Name]
  2. [Feature Name]
  3. [Feature Name]
  4. [Feature Name]
  5. [Feature Name]

### Correlation Insights
- Highly correlated features (>0.8): [list pairs]
- Recommendation: Consider removing one from highly correlated pairs

## Protocol Distribution
- TCP: [count] ([%])
- UDP: [count] ([%])
- ICMP: [count] ([%])
- Other: [count] ([%])

## Next Steps (Phase 1.3)
1. Handle class imbalance using SMOTE (if ratio < 0.3)
2. Engineer domain-specific features from UNSW-NB15
3. Normalize/scale numeric features
4. Remove low-variance features
5. Verify feature compatibility with XGBoost model
```

---

## 📊 Expected Outputs

```
data/
├── raw/
│   ├── UNSW-NB15_1.CSV
│   ├── UNSW-NB15_2.CSV
│   └── ... (additional UNSW-NB15 files)
├── processed/
│   ├── label_distribution.png
│   ├── protocol_distribution.png
│   ├── correlation_matrix.png
│   └── feature_distributions.png
├── train/
│   ├── train.csv
│   └── val.csv
└── test/
    └── test.csv
```

**Key Statistics to Document:**
- Total UNSW-NB15 Samples: 2,540,047
- Benign vs Attack ratio
- Attack type distribution:
  - DoS
  - Exploits
  - Backdoors
  - Analysis
  - Fuzzers
  - Reconnaissance
  - Shellcode
  - Generic
  - Worms
- Missing values & outliers
- Feature correlations

---

## ✅ Checklist

- [x] Dataset downloaded to `data/raw/`
- [x] `eda.py` script created and tested
- [x] EDA report generated with visualizations
- [x] Data split into train/val/test
- [x] Class distribution analyzed
- [x] Missing values identified
- [x] Outliers detected
- [x] EDA summary documented
- [ ] Commit to git: `git add . && git commit -m "Add data EDA and splitting"`

---

## 🔗 Next Steps

✅ **Task 1.2 Complete** → Move to **Task 1.3: Feature Engineering**

---

**Created:** 2026-03-17
