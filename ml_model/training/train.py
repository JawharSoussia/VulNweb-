"""ML Model Training Pipeline"""
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import cross_validate, StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import (
    precision_score, recall_score, f1_score, roc_auc_score,
    confusion_matrix, classification_report
)
import logging
import pickle
import json
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelTrainer:
    """Train and compare multiple models"""

    def __init__(self, train_df, target_col='label'):
        """Initialize with training data"""
        self.train_df = train_df.copy()
        self.target_col = target_col

        # Separate features and target
        self.X = self.train_df.drop(columns=[target_col])
        self.y = self.train_df[target_col]

        self.models = {}
        self.cv_results = {}
        self.best_model = None
        self.best_model_name = None

        logger.info(f"Training data shape: {self.X.shape}")
        logger.info(f"Target distribution: {self.y.value_counts().to_dict()}")

    def train_logistic_regression(self):
        """Train Logistic Regression baseline"""
        logger.info("\n" + "=" * 60)
        logger.info("TRAINING: Logistic Regression")
        logger.info("=" * 60)

        model = LogisticRegression(
            max_iter=1000,
            random_state=42,
            n_jobs=-1,
            solver='lbfgs'
        )

        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        scoring = {
            'precision': 'precision',
            'recall': 'recall',
            'f1': 'f1',
            'roc_auc': 'roc_auc'
        }

        cv_results = cross_validate(
            model, self.X, self.y, cv=cv, scoring=scoring, n_jobs=-1
        )

        self.models['LogisticRegression'] = model
        self.cv_results['LogisticRegression'] = cv_results

        self._print_cv_results('LogisticRegression', cv_results)
        model.fit(self.X, self.y)

    def train_random_forest(self):
        """Train Random Forest"""
        logger.info("\n" + "=" * 60)
        logger.info("TRAINING: Random Forest")
        logger.info("=" * 60)

        model = RandomForestClassifier(
            n_estimators=200,
            max_depth=15,
            min_samples_split=10,
            min_samples_leaf=4,
            random_state=42,
            n_jobs=-1,
            class_weight='balanced'  # Handle imbalance
        )

        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        scoring = {
            'precision': 'precision',
            'recall': 'recall',
            'f1': 'f1',
            'roc_auc': 'roc_auc'
        }

        cv_results = cross_validate(
            model, self.X, self.y, cv=cv, scoring=scoring, n_jobs=-1
        )

        self.models['RandomForest'] = model
        self.cv_results['RandomForest'] = cv_results

        self._print_cv_results('RandomForest', cv_results)
        model.fit(self.X, self.y)

    def train_xgboost(self):
        """Train XGBoost"""
        logger.info("\n" + "=" * 60)
        logger.info("TRAINING: XGBoost")
        logger.info("=" * 60)

        model = XGBClassifier(
            n_estimators=200,
            max_depth=7,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            n_jobs=-1,
            objective='multi:softmax',  # Multi-class classification
            num_class=3
        )

        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        scoring = {
            'precision': 'precision',
            'recall': 'recall',
            'f1': 'f1',
            'roc_auc': 'roc_auc'
        }

        cv_results = cross_validate(
            model, self.X, self.y, cv=cv, scoring=scoring, n_jobs=-1
        )

        self.models['XGBoost'] = model
        self.cv_results['XGBoost'] = cv_results

        self._print_cv_results('XGBoost', cv_results)
        model.fit(self.X, self.y)

    def _print_cv_results(self, model_name, cv_results):
        """Print cross-validation results"""
        for metric in ['precision', 'recall', 'f1', 'roc_auc']:
            scores = cv_results[f'test_{metric}']
            mean_score = np.mean(scores)
            std_score = np.std(scores)
            logger.info(f"{metric.upper():10s}: "
                       f"Mean={mean_score:.4f} ± {std_score:.4f} "
                       f"(folds: {[f'{s:.3f}' for s in scores]})")

    def select_best_model(self):
        """Select best model based on F1-score"""
        logger.info("\n" + "=" * 60)
        logger.info("MODEL COMPARISON")
        logger.info("=" * 60)

        best_f1 = -1
        best_model_name = None

        results_summary = {}

        for model_name, cv_results in self.cv_results.items():
            mean_f1 = np.mean(cv_results['test_f1'])
            mean_recall = np.mean(cv_results['test_recall'])
            mean_precision = np.mean(cv_results['test_precision'])
            mean_auc = np.mean(cv_results['test_roc_auc'])

            results_summary[model_name] = {
                'f1': mean_f1,
                'recall': mean_recall,
                'precision': mean_precision,
                'auc': mean_auc
            }

            logger.info(f"\n{model_name}:")
            logger.info(f"  F1-Score:  {mean_f1:.4f}")
            logger.info(f"  Recall:    {mean_recall:.4f}")
            logger.info(f"  Precision: {mean_precision:.4f}")
            logger.info(f"  ROC-AUC:   {mean_auc:.4f}")

            if mean_f1 > best_f1:
                best_f1 = mean_f1
                best_model_name = model_name

        self.best_model_name = best_model_name
        self.best_model = self.models[best_model_name]

        logger.info(f"\n✓ BEST MODEL: {best_model_name} (F1={best_f1:.4f})")

        return best_model_name, results_summary

    def get_feature_importance(self, top_n=20):
        """Extract feature importance from best model"""
        logger.info("\n" + "=" * 60)
        logger.info("FEATURE IMPORTANCE")
        logger.info("=" * 60)

        importance_method = getattr(self.best_model, 'feature_importances_', None)

        if importance_method is None and hasattr(self.best_model, 'coef_'):
            # For linear models, use absolute coefficient values
            importance = np.abs(self.best_model.coef_[0])
        elif importance_method is not None:
            importance = importance_method
        else:
            logger.warning("Model doesn't support feature importance")
            return {}

        feature_names = self.X.columns
        feature_importance = pd.DataFrame({
            'feature': feature_names,
            'importance': importance
        }).sort_values('importance', ascending=False)

        logger.info(f"\nTop {top_n} Important Features:")
        for idx, row in feature_importance.head(top_n).iterrows():
            logger.info(f"  {row['feature']:30s}: {row['importance']:.4f}")

        return feature_importance

    def train_all_models(self):
        """Train all models"""
        logger.info("\n" + "=" * 60)
        logger.info("STARTING MODEL TRAINING PIPELINE")
        logger.info("=" * 60)

        self.train_logistic_regression()
        self.train_random_forest()
        self.train_xgboost()

        best_model_name, results_summary = self.select_best_model()
        feature_importance = self.get_feature_importance()

        logger.info("\n" + "=" * 60)
        logger.info("✓ TRAINING COMPLETE")
        logger.info("=" * 60)

        return self.best_model, results_summary, feature_importance


if __name__ == "__main__":
    # Load training data
    train_df = pd.read_csv("data/train/train_processed.csv")

    # Train models (note: using 'threat_level' as target column instead of 'label')
    trainer = ModelTrainer(train_df, target_col='threat_level')
    best_model, results, importance = trainer.train_all_models()

    # Save best model
    output_dir = Path("ml_model/training/models")
    output_dir.mkdir(exist_ok=True)

    model_path = output_dir / f"{trainer.best_model_name}_model.pkl"
    with open(model_path, 'wb') as f:
        pickle.dump(best_model, f)

    # Save metadata
    metadata = {
        'model_name': trainer.best_model_name,
        'trained_at': datetime.now().isoformat(),
        'cv_results': {k: v for k, v in results.items()},
        'feature_names': trainer.X.columns.tolist(),
        'target_col': trainer.target_col
    }

    metadata_path = output_dir / "model_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    logger.info(f"\n✓ Model saved to: {model_path}")
    logger.info(f"✓ Metadata saved to: {metadata_path}")