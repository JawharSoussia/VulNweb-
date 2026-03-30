"""Exploratory Data Analysis for malicious_phish URL dataset"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import urllib.parse as urlparse

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)

# Load the dataset
df = pd.read_csv('data/train/train.csv')
print("=" * 80)
print(f"EXPLORATORY DATA ANALYSIS - Malicious Phishing URL Dataset")
print("=" * 80)

# --- 1. DATASET OVERVIEW ---
print(f"\n1. DATASET OVERVIEW")
print(f"   Total records: {len(df):,}")
print(f"   Columns: {df.columns.tolist()}")
print(f"   Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

# --- 2. CLASS DISTRIBUTION ---
print(f"\n2. CLASS DISTRIBUTION")
class_counts = df['type'].value_counts()
class_props = df['type'].value_counts(normalize=True) * 100
for cls in class_counts.index:
    print(f"   {cls:15} : {class_counts[cls]:7,} ({class_props[cls]:6.2f}%)")

# Create class distribution plot
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Pie chart
colors = ['#2ecc71', '#f39c12', '#e74c3c', '#c0392b']
ax1.pie(class_counts.values, labels=class_counts.index, autopct='%1.1f%%',
        colors=colors, startangle=90)
ax1.set_title('Class Distribution (Pie Chart)', fontsize=14, fontweight='bold')

# Bar chart
ax2.bar(class_counts.index, class_counts.values, color=colors)
ax2.set_ylabel('Count', fontsize=11)
ax2.set_title('Class Distribution (Bar Chart)', fontsize=14, fontweight='bold')
ax2.tick_params(axis='x', rotation=45)
for i, v in enumerate(class_counts.values):
    ax2.text(i, v + 5000, f'{v:,}', ha='center', fontweight='bold')

plt.tight_layout()
plt.savefig('data/processed/class_distribution.png', dpi=300, bbox_inches='tight')
print(f"\n   Saved: data/processed/class_distribution.png")
plt.close()

# --- 3. URL CHARACTERISTICS ---
print(f"\n3. URL CHARACTERISTICS")

def extract_url_features(url):
    """Extract basic features from URL"""
    try:
        parsed = urlparse.urlparse(url if url.startswith('http') else f'http://{url}')
        return {
            'url_length': len(url),
            'domain': parsed.netloc if parsed.netloc else urlparse.urlparse(f'http://{url}').netloc,
            'path_length': len(parsed.path),
            'query_length': len(parsed.query),
            'protocol': parsed.scheme if parsed.scheme else 'no_protocol',
            'num_slashes': url.count('/'),
            'num_dots': url.count('.'),
            'num_hyphens': url.count('-'),
            'num_underscores': url.count('_'),
            'num_subdomains': (url.count('.') - 1) if '.' in url else 0,
        }
    except:
        return None

# Extract features for all URLs
print("   Extracting URL features...")
url_features = []
valid_indices = []
for i, url in enumerate(df['url']):
    features = extract_url_features(url)
    if features:
        url_features.append(features)
        valid_indices.append(i)

features_df = pd.DataFrame(url_features)
# Keep only rows with valid features
df = df.iloc[valid_indices].reset_index(drop=True)
print(f"   Valid URLs: {len(df):,} (skipped {len(df) - len(url_features):,} malformed URLs)")

# URL length statistics
print(f"\n   URL LENGTH STATISTICS:")
print(f"      Mean: {features_df['url_length'].mean():.1f} chars")
print(f"      Median: {features_df['url_length'].median():.1f} chars")
print(f"      Min: {features_df['url_length'].min()} chars")
print(f"      Max: {features_df['url_length'].max()} chars")
print(f"      Std: {features_df['url_length'].std():.1f} chars")

# Domain length statistics
print(f"\n   DOMAIN LENGTH STATISTICS:")
print(f"      Mean: {features_df['domain'].str.len().mean():.1f} chars")
print(f"      Median: {features_df['domain'].str.len().median():.1f} chars")

# Protocol distribution
print(f"\n   PROTOCOL DISTRIBUTION:")
protocol_dist = features_df['protocol'].value_counts()
for proto, count in protocol_dist.items():
    print(f"      {proto:20} : {count:7,} ({count/len(features_df)*100:.2f}%)")

# Create URL length distribution plot
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Overall URL length
axes[0, 0].hist(features_df['url_length'], bins=50, color='steelblue', edgecolor='black')
axes[0, 0].set_xlabel('URL Length (characters)')
axes[0, 0].set_ylabel('Frequency')
axes[0, 0].set_title('URL Length Distribution', fontweight='bold')
axes[0, 0].axvline(features_df['url_length'].mean(), color='red', linestyle='--',
                    label=f'Mean: {features_df["url_length"].mean():.0f}')
axes[0, 0].legend()

# URL length by class
df_with_features = df.copy()
df_with_features['url_length'] = features_df['url_length'].values
for cls in df['type'].unique():
    axes[0, 1].hist(df_with_features[df_with_features['type'] == cls]['url_length'],
                    bins=50, alpha=0.6, label=cls)
axes[0, 1].set_xlabel('URL Length')
axes[0, 1].set_ylabel('Frequency')
axes[0, 1].set_title('URL Length Distribution by Class', fontweight='bold')
axes[0, 1].legend()

# Number of dots in URL
axes[1, 0].hist(features_df['num_dots'], bins=range(0, features_df['num_dots'].max() + 2),
                color='coral', edgecolor='black')
axes[1, 0].set_xlabel('Number of Dots')
axes[1, 0].set_ylabel('Frequency')
axes[1, 0].set_title('Number of Dots in URL', fontweight='bold')

# Protocol distribution pie
axes[1, 1].pie(protocol_dist.values, labels=protocol_dist.index, autopct='%1.1f%%')
axes[1, 1].set_title('Protocol Distribution', fontweight='bold')

plt.tight_layout()
plt.savefig('data/processed/url_characteristics.png', dpi=300, bbox_inches='tight')
print(f"   Saved: data/processed/url_characteristics.png")
plt.close()

# --- 4. PATTERN ANALYSIS BY CLASS ---
print(f"\n4. PATTERN ANALYSIS BY CLASS")

for cls in ['benign', 'phishing', 'malware', 'defacement']:
    cls_urls = df[df['type'] == cls]['url'].values
    cls_features = features_df[df['type'] == cls]

    print(f"\n   {cls.upper()}:")
    print(f"      Avg URL length: {cls_features['url_length'].mean():.1f}")
    print(f"      Avg domain length: {cls_features['domain'].str.len().mean():.1f}")
    print(f"      Avg num dots: {cls_features['num_dots'].mean():.2f}")
    print(f"      Avg num slashes: {cls_features['num_slashes'].mean():.2f}")

    # Sample URLs
    print(f"      Sample URLs:")
    for url in cls_urls[:3]:
        print(f"         {url[:70]}...")

# --- 5. MISSING VALUES & DUPLICATES ---
print(f"\n5. DATA QUALITY")
print(f"   Missing values:")
print(f"      URL column: {df['url'].isnull().sum()}")
print(f"      Type column: {df['type'].isnull().sum()}")

duplicates = df['url'].duplicated().sum()
print(f"   Duplicate URLs: {duplicates:,} ({duplicates/len(df)*100:.2f}%)")

# --- 6. SPECIAL CHARACTERS ---
print(f"\n6. SPECIAL CHARACTERS ANALYSIS")

def count_special_chars(url):
    special_chars = '!@#$%^&*()_+-=[]{}|;:,.<>?'
    return sum(1 for char in url if char in special_chars)

special_char_counts = [count_special_chars(url) for url in df['url']]
print(f"   URLs with special characters: {sum(1 for c in special_char_counts if c > 0):,}")
print(f"   Avg special chars per URL: {np.mean(special_char_counts):.2f}")
print(f"   Max special chars: {max(special_char_counts)}")

# --- 7. SUMMARY STATISTICS ---
print(f"\n7. SUMMARY STATISTICS TABLE")
summary_stats = {
    'Statistic': ['Total URLs', 'Unique URLs', 'Duplicates %', 'Avg URL Length',
                  'Benign %', 'Phishing %', 'Malware %', 'Defacement %'],
    'Value': [
        f"{len(df):,}",
        f"{df['url'].nunique():,}",
        f"{duplicates/len(df)*100:.2f}%",
        f"{features_df['url_length'].mean():.1f}",
        f"{class_props['benign']:.2f}%",
        f"{class_props['phishing']:.2f}%",
        f"{class_props['malware']:.2f}%",
        f"{class_props['defacement']:.2f}%",
    ]
}
summary_df = pd.DataFrame(summary_stats)
print(summary_df.to_string(index=False))

print(f"\n" + "=" * 80)
print(f"EDA COMPLETE - Visualizations saved to data/processed/")
print(f"=" * 80)
