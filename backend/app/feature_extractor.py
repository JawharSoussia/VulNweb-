"""URL Feature Extraction for Threat Prediction"""
import numpy as np
import logging
from typing import Dict
from urllib.parse import urlparse
import re

logger = logging.getLogger(__name__)


class URLFeatureExtractor:
    """Extract engineered features from URLs for ML prediction"""

    # Feature names matching Phase 1 feature engineering
    FEATURE_NAMES = [
        'url_length', 'domain_length', 'path_length', 'query_length',
        'fragment_length', 'num_dots_in_domain', 'num_dots_total',
        'num_hyphens', 'num_slashes', 'num_question_marks', 'num_at_symbols',
        'num_colons', 'num_subdomains', 'digit_ratio', 'special_char_ratio',
        'uppercase_ratio', 'lowercase_ratio', 'consonant_ratio', 'has_http',
        'has_https', 'has_ftp', 'has_www', 'has_port', 'is_ip_address',
        'suspicious_keyword_count', 'tld_length', 'domain_entropy',
        'url_entropy', 'has_encoded_chars', 'has_credentials',
        'has_unusual_port', 'long_domain', 'dot_ratio', 'consonant_vowel_ratio',
        'avg_word_length_domain', 'compression_ratio', 'slash_ratio'
    ]

    SUSPICIOUS_KEYWORDS = [
        'admin', 'bin', 'data', 'download', 'dll', 'exe', 'sql', 'etc',
        'passwd', 'phishing', 'malware', 'scam', 'fake', 'verify', 'update',
        'confirm', 'action', 'secure', 'click', 'urgent', 'login', 'signin',
        'paypal', 'amazon', 'apple', 'bank', 'account'
    ]

    def __init__(self):
        """Initialize feature extractor"""
        self.feature_names = self.FEATURE_NAMES

    def extract(self, url: str) -> np.ndarray:
        """Extract all 37 features from URL"""
        try:
            features = {}

            # Parse URL
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            path = parsed.path
            query = parsed.query
            fragment = parsed.fragment
            scheme = parsed.scheme.lower()

            # ================================================================
            # 1. LENGTH FEATURES
            # ================================================================

            features['url_length'] = len(url)
            features['domain_length'] = len(domain)
            features['path_length'] = len(path)
            features['query_length'] = len(query)
            features['fragment_length'] = len(fragment)

            # ================================================================
            # 2. COUNT FEATURES
            # ================================================================

            features['num_dots_in_domain'] = domain.count('.')
            features['num_dots_total'] = url.count('.')
            features['num_hyphens'] = url.count('-')
            features['num_slashes'] = url.count('/')
            features['num_question_marks'] = url.count('?')
            features['num_at_symbols'] = url.count('@')
            features['num_colons'] = url.count(':')

            # ================================================================
            # 3. DERIVED FEATURES
            # ================================================================

            # Subdomains (count dots in domain)
            features['num_subdomains'] = max(0, features['num_dots_in_domain'] - 1)

            # Character type ratios
            digit_count = sum(1 for c in url if c.isdigit())
            uppercase_count = sum(1 for c in url if c.isupper())
            lowercase_count = sum(1 for c in url if c.islower())

            features['digit_ratio'] = digit_count / len(url) if len(url) > 0 else 0
            features['special_char_ratio'] = self._count_special_chars(url) / len(url) if len(url) > 0 else 0
            features['uppercase_ratio'] = uppercase_count / len(url) if len(url) > 0 else 0
            features['lowercase_ratio'] = lowercase_count / len(url) if len(url) > 0 else 0

            # Consonant ratio
            consonants = len(re.findall(r'[bcdfghjklmnprstvwxyz]', url.lower()))
            features['consonant_ratio'] = consonants / len(url) if len(url) > 0 else 0

            # ================================================================
            # 4. PROTOCOL FEATURES (binary)
            # ================================================================

            features['has_http'] = 1.0 if scheme == 'http' else 0.0
            features['has_https'] = 1.0 if scheme == 'https' else 0.0
            features['has_ftp'] = 1.0 if scheme == 'ftp' else 0.0

            # ================================================================
            # 5. DOMAIN STRUCTURE FEATURES
            # ================================================================

            features['has_www'] = 1.0 if domain.startswith('www.') else 0.0
            features['has_port'] = 1.0 if ':' in domain else 0.0
            features['is_ip_address'] = 1.0 if self._is_ip(domain.split(':')[0]) else 0.0

            # ================================================================
            # 6. SUSPICIOUS CONTENT FEATURES
            # ================================================================

            features['suspicious_keyword_count'] = float(
                self._count_suspicious_keywords(url.lower())
            )

            # TLD length
            tld = self._extract_tld(domain)
            features['tld_length'] = len(tld) if tld else 0

            # ================================================================
            # 7. ENTROPY FEATURES
            # ================================================================

            features['domain_entropy'] = self._calculate_entropy(domain)
            features['url_entropy'] = self._calculate_entropy(url)

            # ================================================================
            # 8. ENCODING & CREDENTIAL FEATURES
            # ================================================================

            features['has_encoded_chars'] = 1.0 if '%' in url else 0.0
            features['has_credentials'] = 1.0 if '@' in url and scheme in ['http', 'https'] else 0.0

            # ================================================================
            # 9. PORT FEATURES
            # ================================================================

            features['has_unusual_port'] = 1.0 if self._has_unusual_port(domain) else 0.0

            # ================================================================
            # 10. DOMAIN LENGTH FEATURES
            # ================================================================

            features['long_domain'] = 1.0 if features['domain_length'] > 30 else 0.0

            # ================================================================
            # 11. RATIO FEATURES
            # ================================================================

            features['dot_ratio'] = features['num_dots_total'] / len(url) if len(url) > 0 else 0
            features['slash_ratio'] = features['num_slashes'] / len(url) if len(url) > 0 else 0

            # Consonant-vowel ratio
            vowels = len(re.findall(r'[aeiou]', url.lower()))
            features['consonant_vowel_ratio'] = consonants / (vowels + 1) if (vowels + 1) > 0 else 0

            # Domain word length
            domain_parts = domain.split('.')
            avg_word_len = np.mean([len(part) for part in domain_parts if part]) if domain_parts else 0
            features['avg_word_length_domain'] = avg_word_len

            # ================================================================
            # 12. COMPRESSION RATIO
            # ================================================================

            unique_chars = len(set(url))
            features['compression_ratio'] = unique_chars / len(url) if len(url) > 0 else 0

            # ================================================================
            # CREATE FEATURE VECTOR
            # ================================================================

            feature_vector = np.array([
                features.get(fname, 0.0) for fname in self.FEATURE_NAMES
            ]).reshape(1, -1)

            logger.debug(f"Extracted {len(self.FEATURE_NAMES)} features from URL")
            return feature_vector

        except Exception as e:
            logger.error(f"Error extracting features from URL: {e}")
            raise

    @staticmethod
    def _count_special_chars(text: str) -> int:
        """Count special characters (not alphanumeric or common symbols)"""
        return len(re.findall(r'[^a-zA-Z0-9\-._~:/?#[\]@!$&\'()*+,;=\s]', text))

    @staticmethod
    def _is_ip(s: str) -> bool:
        """Check if string is an IP address"""
        parts = s.split('.')
        if len(parts) != 4:
            return False
        try:
            return all(0 <= int(p) <= 255 for p in parts)
        except ValueError:
            return False

    def _count_suspicious_keywords(self, text: str) -> int:
        """Count suspicious keywords in text"""
        count = 0
        for keyword in self.SUSPICIOUS_KEYWORDS:
            count += text.count(keyword)
        return count

    @staticmethod
    def _extract_tld(domain: str) -> str:
        """Extract TLD from domain"""
        parts = domain.split('.')
        if len(parts) >= 2:
            return parts[-1]
        return ""

    @staticmethod
    def _has_unusual_port(domain: str) -> bool:
        """Check if domain has unusual port"""
        if ':' not in domain:
            return False
        try:
            port = int(domain.split(':')[1])
            # Unusual ports: not 80, 443, 21, 22, 25, 53, 110, 143, 3306, 5432, 8080
            usual_ports = {20, 21, 22, 25, 53, 80, 110, 143, 443, 465, 587, 993, 995,
                          3306, 5432, 8080, 8443}
            return port not in usual_ports
        except (ValueError, IndexError):
            return False

    @staticmethod
    def _calculate_entropy(text: str) -> float:
        """Calculate Shannon entropy of text"""
        if not text:
            return 0.0

        # Count character frequencies
        freq = {}
        for char in text:
            freq[char] = freq.get(char, 0) + 1

        # Calculate entropy
        entropy = 0.0
        length = len(text)
        for count in freq.values():
            p = count / length
            entropy -= p * np.log2(p)

        return entropy

