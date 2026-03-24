"""SMOTE for class imbalance handling"""
import pandas as pd
import numpy as np
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
from sklearn.model_selection import StratifiedKFold, cross_validate
from xgboost import XGBClassifier
import logging
import pickle

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SMOTEHandler:
    """Handle class imbalance using SMOTE"""

    def __init__(self, train_df, val_df, target_col='label'):
        """Initialize with data"""
        self.train_df = train_df.copy()
        self.val_df = val_df.copy()
        self.target_col = target_col

        self.X_train = self.train_df.drop(columns=[target_col])
        self.y_train = self.train_df[target_col]

        self.X_val = self.val_df.drop(columns=[target_col])
        self.y_val = self.val_df[target_col]

        logger.info("SMOTE Handler initialized")
        logger.info(f"Original train target distribution: {self.y_train.value_counts().to_dict()}")

    def analyze_imbalance(self):
        """Analyze class imbalance ratio"""
        logger.info("\n" + "=" * 60)
        logger.info("CLASS IMBALANCE ANALYSIS")
        logger.info("=" * 60)

        counts = self.y_train.value_counts()
        minority_count = counts.min()
        majority_count = counts.max()
        imbalance_ratio = minority_count / majority_count

        logger.info(f"Class 0 (Majority): {majority_count} samples ({majority_count/len(self.y_train)*100:.1f}%)")
        logger.info(f"Class 1 (Minority): {minority_count} samples ({minority_count/len(self.y_train)*100:.1f}%)")
        logger.info(f"Imbalance Ratio: {imbalance_ratio:.4f}")

        if imbalance_ratio < 0.3:
            logger.warning("⚠️  SEVERE IMBALANCE - SMOTE strongly recommended")
        elif imbalance_ratio < 0.5:
            logger.warning("⚠️  Mild imbalance - SMOTE recommended")
        else:
            logger.info("✓ Balanced dataset - SMOTE optional")

        return imbalance_ratio

    def apply_smote(self, k_neighbors=5, random_state=42):
        """Apply SMOTE to training data"""
        logger.info("\n" + "=" * 60)
        logger.info("APPLYING SMOTE")
        logger.info("=" * 60)

        # SMOTE
        smote = SMOTE(k_neighbors=k_neighbors, random_state=random_state)
        self.X_train_smote, self.y_train_smote = smote.fit_resample(
            self.X_train, self.y_train
        )

        # Log new distribution
        unique, counts = np.unique(self.y_train_smote, return_counts=True)
        logger.info("\nAfter SMOTE:")
        for label, count in zip(unique, counts):
            logger.info(f"  Class {label}: {count} samples")

        logger.info(f"✓ Synthetic samples created: {len(self.X_train_smote) - len(self.X_train)}")

        return self.X_train_smote, self.y_train_smote

    def train_with_smote(self):
        """Train model with SMOTE-augmented data"""
        logger.info("\n" + "=" * 60)
        logger.info("TRAINING WITH SMOTE")
        logger.info("=" * 60)

        # Apply SMOTE
        self.apply_smote()

        # Train model
        model = XGBClassifier(
            n_estimators=200,
            max_depth=7,
            learning_rate=0.1,
            random_state=42,
            n_jobs=-1
        )

        model.fit(self.X_train_smote, self.y_train_smote)

        # Evaluate on validation set (without SMOTE)
        from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score

        y_pred = model.predict(self.X_val)
        y_pred_proba = model.predict_proba(self.X_val)[:, 1]

        precision = precision_score(self.y_val, y_pred)
        recall = recall_score(self.y_val, y_pred)
        f1 = f1_score(self.y_val, y_pred)
        auc = roc_auc_score(self.y_val, y_pred_proba)

        logger.info(f"\nValidation Metrics:")
        logger.info(f"  Precision: {precision:.4f}")
        logger.info(f"  Recall:    {recall:.4f} (important for threats!)")
        logger.info(f"  F1-Score:  {f1:.4f}")
        logger.info(f"  ROC-AUC:   {auc:.4f}")

        if recall < 0.9:
            logger.warning("⚠️  Recall < 90% - may miss threats!")

        return model

    def compare_with_without_smote(self):
        """Compare performance with and without SMOTE"""
        logger.info("\n" + "=" * 60)
        logger.info("COMPARING SMOTE vs NO SMOTE")
        logger.info("=" * 60)

        from sklearn.metrics import precision_score, recall_score, f1_score

        # Model WITHOUT SMOTE
        model_no_smote = XGBClassifier(
            n_estimators=200, max_depth=7, learning_rate=0.1, random_state=42, n_jobs=-1
        )
        model_no_smote.fit(self.X_train, self.y_train)

        y_pred_no = model_no_smote.predict(self.X_val)
        precision_no = precision_score(self.y_val, y_pred_no)
        recall_no = recall_score(self.y_val, y_pred_no)
        f1_no = f1_score(self.y_val, y_pred_no)

        # Model WITH SMOTE
        model_with_smote = self.train_with_smote()
        y_pred_yes = model_with_smote.predict(self.X_val)
        precision_yes = precision_score(self.y_val, y_pred_yes)
        recall_yes = recall_score(self.y_val, y_pred_yes)
        f1_yes = f1_score(self.y_val, y_pred_yes)

        # Comparison
        logger.info("\n")
        logger.info(f"{'Metric':<12} {'Without SMOTE':<15} {'With SMOTE':<15} {'Improvement':<15}")
        logger.info("-" * 60)
        logger.info(f"{'Precision':<12} {precision_no:<15.4f} {precision_yes:<15.4f} {(precision_yes-precision_no):+.4f}")
        logger.info(f"{'Recall':<12} {recall_no:<15.4f} {recall_yes:<15.4f} {(recall_yes-recall_no):+.4f}")
        logger.info(f"{'F1-Score':<12} {f1_no:<15.4f} {f1_yes:<15.4f} {(f1_yes-f1_no):+.4f}")

        # Choose best
        if f1_yes > f1_no:
            logger.info(f"\n✓ SMOTE RECOMMENDED - F1 improved by {(f1_yes-f1_no):.4f}")
            return model_with_smote
        else:
            logger.info(f"\n✓ NO SMOTE - Original model better")
            return model_no_smote


if __name__ == "__main__":
    # Load data
    train_df = pd.read_csv("data/train/train_processed.csv")
    val_df = pd.read_csv("data/train/val_processed.csv")

    # Handle imbalance
    handler = SMOTEHandler(train_df, val_df)
    handler.analyze_imbalance()
    best_model = handler.compare_with_without_smote()

    # Save model
    import os
    os.makedirs("ml_model/training/models", exist_ok=True)
    with open("ml_model/training/models/xgboost_smote_model.pkl", 'wb') as f:
        pickle.dump(best_model, f)

    logger.info("\n✓ Model saved!")