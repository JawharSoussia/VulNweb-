"""Data Quality Tests for URL Dataset - Validate processed features"""
import pandas as pd
import numpy as np
import sys


class DataQualityTests:
    """Comprehensive data quality test suite for URL features"""

    def __init__(self):
        self.passed_tests = 0
        self.failed_tests = 0

    def run_test(self, test_name: str, condition: bool, error_msg: str = ""):
        """Run a single test and track results"""
        if condition:
            self.passed_tests += 1
            print(f"  [OK] {test_name}")
        else:
            self.failed_tests += 1
            if error_msg:
                print(f"  [FAIL] {test_name}: {error_msg}")
            else:
                print(f"  [FAIL] {test_name}")

    def test_no_missing_values(self, df):
        """Test that no features have missing values"""
        print("\n[TEST] No Missing Values")
        missing_count = df.isnull().sum().sum()
        self.run_test("No NaN values", missing_count == 0,
                     f"Found {missing_count} NaN values")

        inf_count = np.isinf(df.select_dtypes(include=[np.number])).sum().sum()
        self.run_test("No Infinite values", inf_count == 0,
                     f"Found {inf_count} Inf values")

    def test_feature_dtypes(self, df):
        """Test that features are numeric"""
        print("\n[TEST] Feature Data Types")
        numeric_count = len(df.select_dtypes(include=[np.number]).columns)
        self.run_test(f"Expected number of features", numeric_count >= 37,
                     f"Found {numeric_count} numeric features (expected >= 37)")

    def test_feature_scaling(self, df):
        """Test that features are properly scaled"""
        print("\n[TEST] Feature Scaling")
        numeric_df = df.select_dtypes(include=[np.number])

        min_val = numeric_df.min().min()
        max_val = numeric_df.max().max()

        self.run_test("Features within bounds",
                     min_val >= -10 and max_val <= 10,
                     f"Range: [{min_val:.2f}, {max_val:.2f}]")

    def test_threat_level_distribution(self, df):
        """Test threat levels are distributed"""
        print("\n[TEST] Threat Level Distribution")
        if 'threat_level' not in df.columns:
            print("  [!] threat_level column not found")
            return

        threat_counts = df['threat_level'].value_counts().sort_index()
        self.run_test("All threat levels present",
                     set(threat_counts.index) == {0, 1, 2},
                     f"Threat levels found: {set(threat_counts.index)}")

    def test_split_sizes(self, train_df, val_df, test_df):
        """Test data splits are approximately 60/20/20"""
        print("\n[TEST] Split Sizes (60/20/20)")
        total = len(train_df) + len(val_df) + len(test_df)

        train_pct = len(train_df) / total * 100
        val_pct = len(val_df) / total * 100
        test_pct = len(test_df) / total * 100

        self.run_test("Train ~60%", 58 <= train_pct <= 62,
                     f"Train: {train_pct:.1f}%")
        self.run_test("Val ~20%", 18 <= val_pct <= 22,
                     f"Val: {val_pct:.1f}%")
        self.run_test("Test ~20%", 18 <= test_pct <= 22,
                     f"Test: {test_pct:.1f}%")

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.failed_tests}")
        print(f"Total:  {self.passed_tests + self.failed_tests}")

        if self.failed_tests == 0:
            print("\n[SUCCESS] ALL TESTS PASSED!")
            return True
        else:
            print(f"\n[WARNING] {self.failed_tests} TEST(S) FAILED")
            return False


def main():
    print("=" * 80)
    print("DATA QUALITY TEST SUITE - URL Features Dataset")
    print("=" * 80)

    # Load datasets
    print("\nLoading processed datasets...")
    train_df = pd.read_csv('data/train/train_processed.csv')
    val_df = pd.read_csv('data/val/val_processed.csv')
    test_df = pd.read_csv('data/test/test_processed.csv')

    print(f"  Train: {train_df.shape}")
    print(f"  Val:   {val_df.shape}")
    print(f"  Test:  {test_df.shape}")

    tester = DataQualityTests()

    print("\n" + "=" * 80)
    print("RUNNING TESTS")
    print("=" * 80)

    tester.test_no_missing_values(train_df)
    tester.test_no_missing_values(val_df)
    tester.test_no_missing_values(test_df)
    tester.test_feature_dtypes(train_df)
    tester.test_feature_scaling(train_df)
    tester.test_threat_level_distribution(train_df)
    tester.test_threat_level_distribution(val_df)
    tester.test_threat_level_distribution(test_df)
    tester.test_split_sizes(train_df, val_df, test_df)

    all_passed = tester.print_summary()
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
