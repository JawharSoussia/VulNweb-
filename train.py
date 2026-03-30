"""Ensemble Model Training - XGBoost + Logistic Regression + Random Forest"""
import pandas as pd
import numpy as np
from sklearn.model_selection import cross_validate, StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import (
    classification_report, confusion_matrix, accuracy_score,
    precision_recall_fscore_support
)
import matplotlib.pyplot as plt
import pickle
import warnings
warnings.filterwarnings('ignore')

class EnsembleTrainer:
    """Train and evaluate ensemble of 3 models"""

    def __init__(self, random_state=42):
        self.random_state = random_state
        self.models = {}
        self.cv_results = {}
        self.feature_importance = {}

    def create_models(self):
        """Create 3 base models with class weighting"""
        print("Creating base models with class_weight='balanced'...")

        self.models['xgboost'] = XGBClassifier(
            objective='multi:softmax',
            num_class=3,
            max_depth=6,
            learning_rate=0.1,
            n_estimators=100,
            random_state=self.random_state,
            n_jobs=-1,
            verbosity=0
        )

        self.models['logistic_regression'] = LogisticRegression(
            multi_class='multinomial',
            max_iter=500,
            class_weight='balanced',
            random_state=self.random_state,
            n_jobs=-1,
            solver='lbfgs'
        )

        self.models['random_forest'] = RandomForestClassifier(
            n_estimators=100,
            max_depth=15,
            class_weight='balanced',
            random_state=self.random_state,
            n_jobs=-1
        )

        print("Models created successfully")
        return self.models

    def cross_validate_models(self, X, y, cv=5):
        """Cross-validate all models"""
        print(f"\nPerforming {cv}-fold cross-validation...")

        skf = StratifiedKFold(n_splits=cv, shuffle=True, random_state=self.random_state)

        scoring = {
            'accuracy': 'accuracy',
            'precision_macro': 'precision_macro',
            'recall_macro': 'recall_macro',
            'f1_macro': 'f1_macro',
        }

        for name, model in self.models.items():
            print(f"\n  Training {name}...")
            cv_results = cross_validate(model, X, y, cv=skf, scoring=scoring,
                                       return_train_score=True, n_jobs=-1)

            self.cv_results[name] = cv_results

            print(f"    Accuracy: {cv_results['test_accuracy'].mean():.4f} (+/- {cv_results['test_accuracy'].std():.4f})")
            print(f"    F1-Score: {cv_results['test_f1_macro'].mean():.4f} (+/- {cv_results['test_f1_macro'].std():.4f})")

    def train_final_models(self, X_train, y_train):
        """Train final models on full training set"""
        print("\nTraining final models on full training set...")

        for name, model in self.models.items():
            print(f"  Training {name}...")
            model.fit(X_train, y_train)

            if hasattr(model, 'feature_importances_'):
                self.feature_importance[name] = model.feature_importances_
            elif hasattr(model, 'coef_'):
                self.feature_importance[name] = np.abs(model.coef_).mean(axis=0)

        print("Final models trained successfully")

    def evaluate_on_test_set(self, X_test, y_test, feature_names):
        """Evaluate all models on test set"""
        print("\n" + "=" * 80)
        print("TEST SET EVALUATION")
        print("=" * 80)

        results = {}

        for name, model in self.models.items():
            print(f"\n{name.upper()}")
            print("-" * 40)

            y_pred = model.predict(X_test)
            y_pred_proba = model.predict_proba(X_test)

            accuracy = accuracy_score(y_test, y_pred)
            precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='macro')

            print(f"Accuracy:  {accuracy:.4f}")
            print(f"Precision: {precision:.4f}")
            print(f"Recall:    {recall:.4f}")
            print(f"F1-Score:  {f1:.4f}")

            print(f"\nPer-class metrics:")
            report = classification_report(y_test, y_pred,
                                          target_names=['safe', 'suspicious', 'critical'],
                                          digits=4)
            print(report)

            if name in self.feature_importance:
                importance = self.feature_importance[name]
                top_indices = np.argsort(importance)[-10:][::-1]
                print(f"\nTop 10 important features:")
                for i, idx in enumerate(top_indices, 1):
                    print(f"  {i:2d}. {feature_names[idx]:30s} ({importance[idx]:.4f})")

            cm = confusion_matrix(y_test, y_pred)
            print(f"\nConfusion Matrix:")
            print(cm)

            results[name] = {
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1': f1,
                'predictions': y_pred,
                'probabilities': y_pred_proba,
                'confusion_matrix': cm
            }

        return results

    def ensemble_voting(self, X_test, y_test):
        """Hard voting ensemble"""
        print("\n" + "=" * 80)
        print("ENSEMBLE VOTING (HARD VOTING - 3 MODELS)")
        print("=" * 80)

        predictions = []
        for name, model in self.models.items():
            pred = model.predict(X_test)
            predictions.append(pred)

        predictions_array = np.array(predictions)
        ensemble_pred = np.apply_along_axis(lambda x: np.bincount(x).argmax(), axis=0, arr=predictions_array)

        proba = []
        for name, model in self.models.items():
            proba.append(model.predict_proba(X_test))

        avg_proba = np.mean(proba, axis=0)
        ensemble_pred_soft = np.argmax(avg_proba, axis=1)

        accuracy_hard = accuracy_score(y_test, ensemble_pred)
        precision_hard, recall_hard, f1_hard, _ = precision_recall_fscore_support(
            y_test, ensemble_pred, average='macro')

        print(f"\nHard Voting Results:")
        print(f"  Accuracy:  {accuracy_hard:.4f}")
        print(f"  Precision: {precision_hard:.4f}")
        print(f"  Recall:    {recall_hard:.4f}")
        print(f"  F1-Score:  {f1_hard:.4f}")

        accuracy_soft = accuracy_score(y_test, ensemble_pred_soft)
        precision_soft, recall_soft, f1_soft, _ = precision_recall_fscore_support(
            y_test, ensemble_pred_soft, average='macro')

        print(f"\nSoft Voting Results:")
        print(f"  Accuracy:  {accuracy_soft:.4f}")
        print(f"  Precision: {precision_soft:.4f}")
        print(f"  Recall:    {recall_soft:.4f}")
        print(f"  F1-Score:  {f1_soft:.4f}")

        return {
            'hard_voting': ensemble_pred,
            'soft_voting': ensemble_pred_soft,
            'avg_proba': avg_proba,
            'hard_accuracy': accuracy_hard,
            'soft_accuracy': accuracy_soft
        }

    def save_models(self, output_dir='ml_model/inference/models'):
        """Save all trained models"""
        print(f"\nSaving models to {output_dir}/...")

        import os
        os.makedirs(output_dir, exist_ok=True)

        for name, model in self.models.items():
            path = f'{output_dir}/{name}_model.pkl'
            with open(path, 'wb') as f:
                pickle.dump(model, f)
            print(f"  Saved: {path}")

        path = f'{output_dir}/feature_importance.pkl'
        with open(path, 'wb') as f:
            pickle.dump(self.feature_importance, f)
        print(f"  Saved: {path}")


def main():
    print("=" * 80)
    print("ENSEMBLE MODEL TRAINING - URL Threat Detection")
    print("=" * 80)

    print("\nLoading datasets...")
    train_df = pd.read_csv('data/train/train_processed.csv')
    test_df = pd.read_csv('data/test/test_processed.csv')

    print(f"  Train: {train_df.shape}")
    print(f"  Test:  {test_df.shape}")

    feature_cols = [col for col in train_df.columns if col != 'threat_level']
    X_train = train_df[feature_cols].values
    y_train = train_df['threat_level'].values
    X_test = test_df[feature_cols].values
    y_test = test_df['threat_level'].values

    print(f"\nFeatures: {len(feature_cols)}")
    print(f"Classes: {len(np.unique(y_train))}")
    print(f"Class distribution (train): {np.bincount(y_train.astype(int))}")
    print(f"Class distribution (test):  {np.bincount(y_test.astype(int))}")

    trainer = EnsembleTrainer()
    trainer.create_models()
    trainer.cross_validate_models(X_train, y_train, cv=5)
    trainer.train_final_models(X_train, y_train)
    test_results = trainer.evaluate_on_test_set(X_test, y_test, feature_cols)
    ensemble_results = trainer.ensemble_voting(X_test, y_test)
    trainer.save_models()

    print("\n" + "=" * 80)
    print("TRAINING SUMMARY")
    print("=" * 80)
    print(f"Models trained:           3 (XGBoost, LogisticReg, RandomForest)")
    print(f"CV folds:                 5")
    print(f"Test set accuracy (XGB):  {test_results['xgboost']['accuracy']:.4f}")
    print(f"Ensemble accuracy (hard): {ensemble_results['hard_accuracy']:.4f}")
    print(f"Ensemble accuracy (soft): {ensemble_results['soft_accuracy']:.4f}")
    print(f"\nModels saved to: ml_model/inference/models/")
    print("=" * 80)


if __name__ == "__main__":
    main()
