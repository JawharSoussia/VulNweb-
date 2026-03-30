"""URL Feature Engineering Pipeline - Extract 40+ lexical features from URLs"""
import pandas as pd
import numpy as np
import urllib.parse as urlparse
from urllib.parse import urlparse as parse_url
import string
import pickle
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class URLFeatureEngineer:
    """Extract lexical and heuristic features from URLs"""

    SUSPICIOUS_KEYWORDS = [
        'free', 'secure', 'verify', 'confirm', 'update', 'click', 'login',
        'urgent', 'suspended', 'account', 'action', 'activity', 'security',
        'information', 'confirm', 'authenticate', 'paypal', 'ebay', 'amazon',
        'apple', 'adobe', 'microsoft', 'google', 'facebook', 'twitter',
        'admin', 'cp', 'wp-admin', 'phpmyadmin', 'cpanel'
    ]

    def __init__(self):
        self.scaler = StandardScaler()
        self.feature_names = []

    def extract_features(self, url):
        """Extract all features from a single URL"""
        features = {}

        try:
            # Parse URL with better error handling
            try:
                if not url.startswith(('http://', 'https://', 'ftp://')):
                    parsed = parse_url(f'http://{url}')
                else:
                    parsed = parse_url(url)
            except (ValueError, AttributeError):
                # If URL parsing fails, try with less strict parsing
                parsed = parse_url(f'http://{url}') if not url.startswith('http') else parse_url(url)

            # 1. LENGTH FEATURES (5 features)
            features['url_length'] = len(url)
            domain = parsed.netloc if parsed.netloc else parse_url(f'http://{url}').netloc
            features['domain_length'] = len(domain)
            features['path_length'] = len(parsed.path)
            features['query_length'] = len(parsed.query)
            features['fragment_length'] = len(parsed.fragment)

            # 2. STRUCTURAL FEATURES (8 features)
            features['num_dots_in_domain'] = domain.count('.')
            features['num_dots_total'] = url.count('.')
            features['num_hyphens'] = url.count('-')
            features['num_slashes'] = url.count('/')
            features['num_question_marks'] = url.count('?')
            features['num_at_symbols'] = url.count('@')
            features['num_colons'] = url.count(':')
            features['num_subdomains'] = max(0, domain.count('.') - 1)

            # 3. CHARACTER DISTRIBUTION (5 features)
            digits = sum(1 for c in url if c.isdigit())
            features['digit_ratio'] = digits / len(url) if len(url) > 0 else 0

            special_chars = sum(1 for c in url if c in '!@#$%^&*()_+-=[]{}|;:,.<>?/\\')
            features['special_char_ratio'] = special_chars / len(url) if len(url) > 0 else 0

            uppercase = sum(1 for c in url if c.isupper())
            features['uppercase_ratio'] = uppercase / len(url) if len(url) > 0 else 0

            lowercase = sum(1 for c in url if c.islower())
            features['lowercase_ratio'] = lowercase / len(url) if len(url) > 0 else 0

            # Consonant ratio (approximate)
            vowels = 'aeiouAEIOU'
            consonants = sum(1 for c in url if c.isalpha() and c not in vowels)
            total_alpha = sum(1 for c in url if c.isalpha())
            features['consonant_ratio'] = consonants / total_alpha if total_alpha > 0 else 0

            # 4. PROTOCOL/DOMAIN FEATURES (6 features)
            protocol = parsed.scheme if parsed.scheme else 'none'
            features['has_http'] = 1.0 if protocol == 'http' else 0.0
            features['has_https'] = 1.0 if protocol == 'https' else 0.0
            features['has_ftp'] = 1.0 if protocol == 'ftp' else 0.0
            features['has_www'] = 1.0 if domain.startswith('www') else 0.0
            features['has_port'] = 1.0 if ':' in domain else 0.0

            # 5. HEURISTIC RED FLAGS (10 features)
            # IP address detector
            ip_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
            features['is_ip_address'] = 1.0 if self._is_ip(domain) else 0.0

            # Suspicious keywords
            url_lower = url.lower()
            suspicious_count = sum(1 for kw in self.SUSPICIOUS_KEYWORDS if kw in url_lower)
            features['suspicious_keyword_count'] = suspicious_count

            # TLD length
            tld = domain.split('.')[-1] if '.' in domain else domain
            features['tld_length'] = len(tld)

            # Entropy approximation (domain entropy)
            features['domain_entropy'] = self._calculate_entropy(domain)

            # URL entropy
            features['url_entropy'] = self._calculate_entropy(url)

            # Has encoded characters
            features['has_encoded_chars'] = 1.0 if '%' in url else 0.0

            # Has credentials marker
            features['has_credentials'] = 1.0 if '@' in parsed.netloc else 0.0

            # Has unusual port
            try:
                if ':' in domain:
                    port = int(domain.split(':')[-1])
                    features['has_unusual_port'] = 1.0 if port not in [80, 443, 21, 22] else 0.0
                else:
                    features['has_unusual_port'] = 0.0
            except:
                features['has_unusual_port'] = 0.0

            # Long domain name (suspicious)
            features['long_domain'] = 1.0 if len(domain) > 30 else 0.0

            # 6. DERIVED METRICS (5 features)
            dot_ratio = url.count('.') / len(url) if len(url) > 0 else 0
            features['dot_ratio'] = dot_ratio

            consonant_vowel_ratio = consonants / (total_alpha - consonants) if (total_alpha - consonants) > 0 else 0
            features['consonant_vowel_ratio'] = consonant_vowel_ratio

            # Average word length in domain (split by dots and hyphens)
            domain_parts = domain.replace('.', ' ').replace('-', ' ').split()
            avg_word_length = np.mean([len(p) for p in domain_parts]) if domain_parts else 0
            features['avg_word_length_domain'] = avg_word_length

            # Compression ratio (indicator of obfuscation)
            try:
                import zlib
                compressed_size = len(zlib.compress(url.encode()))
                compression_ratio = compressed_size / len(url) if len(url) > 0 else 0
                features['compression_ratio'] = compression_ratio
            except:
                features['compression_ratio'] = 0.5

            # Multiple slashes ratio
            features['slash_ratio'] = url.count('/') / len(url) if len(url) > 0 else 0

            return features

        except Exception as e:
            # Silently skip URLs that fail to process
            return None

    @staticmethod
    def _is_ip(domain):
        """Check if domain is an IP address"""
        parts = domain.split(':')[0].split('.')
        if len(parts) != 4:
            return False
        try:
            return all(0 <= int(p) <= 255 for p in parts)
        except:
            return False

    @staticmethod
    def _calculate_entropy(s):
        """Calculate Shannon entropy of a string"""
        if not s:
            return 0
        entropy = 0
        for char in set(s):
            p = s.count(char) / len(s)
            entropy -= p * np.log2(p)
        return entropy

    def fit_transform(self, df):
        """Extract features and fit scaler"""
        print(f"Extracting features from {len(df)} URLs...")

        features_list = []
        valid_indices = []

        for i, url in enumerate(df['url']):
            features = self.extract_features(url)
            if features:
                features_list.append(features)
                valid_indices.append(i)

            if (i + 1) % 50000 == 0:
                print(f"  Processed {i + 1:,} URLs...")

        features_df = pd.DataFrame(features_list)
        self.feature_names = features_df.columns.tolist()

        print(f"Extracted {len(self.feature_names)} features from {len(features_df)} URLs")
        print(f"Features: {self.feature_names}")

        # Clip extreme outliers before scaling
        print("Clipping outliers...")
        for col in features_df.columns:
            Q1 = features_df[col].quantile(0.25)
            Q3 = features_df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 3 * IQR
            upper_bound = Q3 + 3 * IQR
            features_df[col] = features_df[col].clip(lower_bound, upper_bound)

        # Scale features
        print("Scaling features...")
        scaled_features = self.scaler.fit_transform(features_df)

        # Clip scaled features to [-10, 10]
        scaled_features = np.clip(scaled_features, -10, 10)

        # Create result dataframe
        result = df.iloc[valid_indices].reset_index(drop=True).copy()
        for i, col in enumerate(self.feature_names):
            result[col] = scaled_features[:, i]

        # Convert threat types to threat levels
        threat_mapping = {
            'benign': 0,
            'defacement': 1,
            'phishing': 2,
            'malware': 2
        }
        result['threat_level'] = result['type'].map(threat_mapping)

        # Drop original columns
        result = result.drop(['url', 'type'], axis=1)

        return result

    def transform(self, df):
        """Transform data using fitted scaler"""
        print(f"Extracting features from {len(df)} URLs...")

        features_list = []
        valid_indices = []

        for i, url in enumerate(df['url']):
            features = self.extract_features(url)
            if features:
                features_list.append(features)
                valid_indices.append(i)

            if (i + 1) % 50000 == 0:
                print(f"  Processed {i + 1:,} URLs...")

        features_df = pd.DataFrame(features_list)[self.feature_names]

        # Clip extreme outliers before scaling (using same bounds as training)
        for col in features_df.columns:
            Q1 = features_df[col].quantile(0.25)
            Q3 = features_df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 3 * IQR
            upper_bound = Q3 + 3 * IQR
            features_df[col] = features_df[col].clip(lower_bound, upper_bound)

        # Scale features using fitted scaler
        print("Scaling features...")
        scaled_features = self.scaler.transform(features_df)

        # Clip scaled features to [-10, 10]
        scaled_features = np.clip(scaled_features, -10, 10)

        # Create result dataframe
        result = df.iloc[valid_indices].reset_index(drop=True).copy()
        for i, col in enumerate(self.feature_names):
            result[col] = scaled_features[:, i]

        # Convert threat types to threat levels
        threat_mapping = {
            'benign': 0,
            'defacement': 1,
            'phishing': 2,
            'malware': 2
        }
        result['threat_level'] = result['type'].map(threat_mapping)

        # Drop original columns
        result = result.drop(['url', 'type'], axis=1)

        return result


def main():
    print("=" * 80)
    print("URL FEATURE ENGINEERING PIPELINE")
    print("=" * 80)

    # Load data
    print("\nLoading datasets...")
    train_df = pd.read_csv('data/train/train.csv')
    val_df = pd.read_csv('data/val/val.csv')
    test_df = pd.read_csv('data/test/test.csv')

    print(f"  Train: {len(train_df)} URLs")
    print(f"  Val: {len(val_df)} URLs")
    print(f"  Test: {len(test_df)} URLs")

    # Initialize engineer and fit on training data
    engineer = URLFeatureEngineer()

    print("\n" + "=" * 80)
    print("TRAINING SET - Extracting and Fitting Scaler")
    print("=" * 80)
    train_processed = engineer.fit_transform(train_df)

    print("\n" + "=" * 80)
    print("VALIDATION SET - Extracting")
    print("=" * 80)
    val_processed = engineer.transform(val_df)

    print("\n" + "=" * 80)
    print("TEST SET - Extracting")
    print("=" * 80)
    test_processed = engineer.transform(test_df)

    # Save processed datasets
    print("\nSaving processed datasets...")
    train_processed.to_csv('data/train/train_processed.csv', index=False)
    val_processed.to_csv('data/val/val_processed.csv', index=False)
    test_processed.to_csv('data/test/test_processed.csv', index=False)

    print("\nProcessed datasets saved:")
    print(f"  - data/train/train_processed.csv ({train_processed.shape})")
    print(f"  - data/val/val_processed.csv ({val_processed.shape})")
    print(f"  - data/test/test_processed.csv ({test_processed.shape})")

    # Save preprocessor
    print("\nSaving preprocessor and feature names...")
    preprocessor_data = {
        'scaler': engineer.scaler,
        'feature_names': engineer.feature_names,
        'threat_levels': {0: 'safe', 1: 'suspicious', 2: 'critical'}
    }
    with open('ml_model/training/feature_preprocessor.pkl', 'wb') as f:
        pickle.dump(preprocessor_data, f)
    print(f"  - ml_model/training/feature_preprocessor.pkl")

    # Display statistics
    print("\n" + "=" * 80)
    print("FEATURE STATISTICS")
    print("=" * 80)
    print(f"Total features extracted: {len(engineer.feature_names)}")
    print(f"\nFeatures:")
    for i, fname in enumerate(engineer.feature_names, 1):
        print(f"  {i:2d}. {fname}")

    print(f"\n{'-' * 80}")
    print("PROCESSED DATA STATISTICS")
    print(f"{'-' * 80}")
    print(f"\nTrain split:")
    print(f"  Shape: {train_processed.shape}")
    print(f"  Threat level distribution (train):")
    print(train_processed['threat_level'].value_counts().sort_index())

    print(f"\nVal split:")
    print(f"  Shape: {val_processed.shape}")
    print(f"  Threat level distribution (val):")
    print(val_processed['threat_level'].value_counts().sort_index())

    print(f"\nTest split:")
    print(f"  Shape: {test_processed.shape}")
    print(f"  Threat level distribution (test):")
    print(test_processed['threat_level'].value_counts().sort_index())

    print("\n" + "=" * 80)
    print("FEATURE ENGINEERING COMPLETE!")
    print("=" * 80)


if __name__ == "__main__":
    main()
