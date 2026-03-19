"""Exploratory Data Analysis for UNSW-NB15 Dataset"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for file saving
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

class DataAnalyzer:
    """Perform comprehensive EDA on UNSW-NB15 dataset"""

    def __init__(self):
        """Initialize and load UNSW-NB15 CSV files"""
        logger.info("Loading UNSW-NB15 dataset files...")
        csv_files = sorted(glob(str(DATA_RAW_PATH / "*.csv")))

        if not csv_files:
            logger.error(" No CSV files found in data/raw/")
            raise FileNotFoundError("Please download UNSW-NB15 dataset to data/raw/")

        # Load all CSV files (they're often split across multiple files)
        df_list = []
        for csv_file in csv_files:
            logger.info(f"Loading: {Path(csv_file).name}")
            df = pd.read_csv(
                csv_file,
                names=UNSW_COLUMNS,
                low_memory=False
            )

            # Drop the extra Kaggle index columns
            df = df.drop(['Unnamed_0', 'Unnamed_1'], axis=1, errors='ignore')

            # Convert numeric columns (handle hex values like 0xc0a8)
            # Keep categorical columns as strings: srcip, dstip, service, state, proto, attack
            numeric_cols = [col for col in df.columns
                           if col not in ['srcip', 'dstip', 'service', 'state', 'proto', 'attack', 'label']]
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            # Make sure proto stays as string
            df['proto'] = df['proto'].astype(str).str.lower().fillna('unknown')

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
            plt.close()
            logger.info(f"✓ Saved: label_distribution.png")

            # Check class imbalance
            ratio = label_counts.min() / label_counts.max()
            logger.warning(f"Class Imbalance Ratio: {ratio:.2f} (1 = balanced)")
            if ratio < 0.3:
                logger.warning("SEVERE IMBALANCE - Will use SMOTE in Phase 2")

    def correlation_analysis(self):
        """Analyze feature correlations on sample for performance"""
        logger.info("=" * 60)
        logger.info("CORRELATION ANALYSIS (Top Features - Sampled)")
        logger.info("=" * 60)

        numeric_df = self.df.select_dtypes(include=[np.number])

        if len(numeric_df.columns) > 1:
            # Sample 50k rows for correlation to avoid memory/speed issues
            sample_size = min(50000, len(numeric_df))
            sample_df = numeric_df.sample(n=sample_size, random_state=42)
            logger.info(f"Computing correlation on {sample_size:,} samples...")

            corr_matrix = sample_df.corr()

            # Plot correlation heatmap (sample of top features)
            top_vars = numeric_df.var().nlargest(15).index
            plt.figure(figsize=(12, 10))
            sns.heatmap(corr_matrix.loc[top_vars, top_vars], cmap='coolwarm',
                       center=0, square=True, annot=False)
            plt.title('Top 15 Features - Correlation Matrix (50k sample)')
            plt.tight_layout()
            plt.savefig(f'{DATA_PROCESSED_PATH}/correlation_matrix.png')
            plt.close()
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
        """Detect outliers in numeric features (sampled for speed)"""
        logger.info("=" * 60)
        logger.info("OUTLIER DETECTION (IQR Method - Sampled)")
        logger.info("=" * 60)

        numeric_df = self.df.select_dtypes(include=[np.number])

        # Sample for speed (outliers consistent across samples)
        sample_size = min(100000, len(numeric_df))
        sample_df = numeric_df.sample(n=sample_size, random_state=42)
        logger.info(f"Analyzing outliers on {sample_size:,} samples...")

        outlier_counts = {}

        for col in sample_df.columns:
            Q1 = sample_df[col].quantile(0.25)
            Q3 = sample_df[col].quantile(0.75)
            IQR = Q3 - Q1

            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            outliers = ((sample_df[col] < lower_bound) |
                       (sample_df[col] > upper_bound)).sum()
            outlier_counts[col] = outliers

        outlier_cols = {k: v for k, v in outlier_counts.items() if v > 0}
        if outlier_cols:
            logger.warning("Top 10 columns with outliers:")
            for col, count in sorted(outlier_cols.items(),
                                    key=lambda x: x[1], reverse=True)[:10]:
                pct = (count / sample_size * 100)
                logger.warning(f"  {col}: {count} ({pct:.2f}%)")
        else:
            logger.info("✓ No significant outliers detected")

    def protocol_analysis(self):
        """Analyze protocol distribution (UNSW-NB15 specific)"""
        logger.info("=" * 60)
        logger.info("PROTOCOL DISTRIBUTION (UNSW-NB15)")
        logger.info("=" * 60)

        if 'proto' in self.df.columns:
            # Standardize protocol names - map various forms to standard names
            def standardize_protocol(proto):
                if pd.isna(proto):
                    return 'Unknown'
                proto_str = str(proto).lower().strip()

                # Map to standard protocol names
                if proto_str in ['tcp', '6', 'tcp ']:
                    return 'TCP'
                elif proto_str in ['udp', '17', 'udp ']:
                    return 'UDP'
                elif proto_str in ['icmp', '1', 'icmp ']:
                    return 'ICMP'
                else:
                    return 'Other'

            # Create standardized protocol column
            proto_std = self.df['proto'].apply(standardize_protocol)
            proto_counts = proto_std.value_counts()

            # Log protocol distribution
            logger.info("\nProtocol Distribution:")
            total = self.df.shape[0]

            # Ensure proper order: TCP, UDP, ICMP, Other
            proto_order = ['TCP', 'UDP', 'ICMP', 'Other']
            for proto_name in proto_order:
                if proto_name in proto_counts.index:
                    count = proto_counts[proto_name]
                    pct = (count / total * 100)
                    logger.info(f"- {proto_name}: {count:,} ({pct:.2f}%)")

            # Create visualization
            proto_series = proto_counts.reindex(proto_order, fill_value=0)
            plt.figure(figsize=(10, 6))
            colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
            proto_series.plot(kind='bar', color=colors)
            plt.title('Protocol Distribution (UNSW-NB15)')
            plt.xlabel('Protocol')
            plt.ylabel('Count')
            plt.xticks(rotation=0)
            plt.tight_layout()
            plt.savefig(f'{DATA_PROCESSED_PATH}/protocol_distribution.png', dpi=100)
            plt.close()
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
        logger.error(f"EDA failed: {e}")
        raise