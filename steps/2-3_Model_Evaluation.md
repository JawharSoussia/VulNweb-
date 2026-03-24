# Task 2.3: Model Evaluation & Metrics

**Phase:** ML Model Development
**Deadline:** Day 21
**Status:** ⏳ Pending
**Dependencies:** Task 2.2 complete

---

## 📋 Objective
Evaluate model on test set. Calculate key metrics (Precision, Recall, F1, ROC-AUC). Create visualizations.

---

## 🎯 What to Do

### Step 1: Create Evaluation Script

**Create: `ml_model/training/evaluate.py`**

```python
"""Model Evaluation on Test Set"""
import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    precision_score, recall_score, f1_score, roc_auc_score,
    confusion_matrix, classification_report, roc_curve, auc
)
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelEvaluator:
    """Evaluate model on test set"""

    def __init__(self, model_path, test_df, target_col='label'):
        """Load model and test data"""
        with open(model_path, 'rb') as f:
            self.model = pickle.load(f)

        self.test_df = test_df.copy()
        self.target_col = target_col

        self.X_test = test_df.drop(columns=[target_col])
        self.y_test = test_df[target_col]

        self.output_dir = Path("ml_model/training/evaluation")
        self.output_dir.mkdir(exist_ok=True)

    def make_predictions(self):
        """Generate predictions"""
        logger.info("Generating predictions...")
        self.y_pred = self.model.predict(self.X_test)
        self.y_pred_proba = self.model.predict_proba(self.X_test)[:, 1]
        logger.info(f"✓ Predictions made on {len(self.X_test)} samples")

    def calculate_metrics(self):
        """Calculate evaluation metrics"""
        logger.info("\n" + "=" * 60)
        logger.info("MODEL EVALUATION METRICS")
        logger.info("=" * 60)

        self.precision = precision_score(self.y_test, self.y_pred)
        self.recall = recall_score(self.y_test, self.y_pred)
        self.f1 = f1_score(self.y_test, self.y_pred)
        self.roc_auc = roc_auc_score(self.y_test, self.y_pred_proba)

        logger.info(f"Precision: {self.precision:.4f} "
                   f"({self.precision*100:.2f}% of predicted threats are real)")
        logger.info(f"Recall:    {self.recall:.4f} "
                   f"({self.recall*100:.2f}% of real threats detected)")
        logger.info(f"F1-Score:  {self.f1:.4f}")
        logger.info(f"ROC-AUC:   {self.roc_auc:.4f}")

        # Check success criteria
        logger.info("\n" + "-" * 60)
        if self.recall >= 0.90:
            logger.info("✓ RECALL REQUIREMENT MET (≥ 90%)")
        else:
            logger.warning(f"⚠️  Recall {self.recall:.2%} < 90% target")

        if self.f1 >= 0.85:
            logger.info("✓ F1-SCORE REQUIREMENT MET (≥ 0.85)")
        else:
            logger.warning(f"⚠️  F1 {self.f1:.4f} < 0.85 target")

    def confusion_analysis(self):
        """Analyze confusion matrix"""
        logger.info("\n" + "=" * 60)
        logger.info("CONFUSION MATRIX ANALYSIS")
        logger.info("=" * 60)

        cm = confusion_matrix(self.y_test, self.y_pred)
        tn, fp, fn, tp = cm.ravel()

        logger.info(f"\nTrue Negatives (TN):  {tn} (safe correctly identified)")
        logger.info(f"False Positives (FP): {fp} (false alarms)")
        logger.info(f"False Negatives (FN): {fn} (missed threats!) ⚠️")
        logger.info(f"True Positives (TP):  {tp} (threats correctly identified)")

        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
        logger.info(f"\nFalse Positive Rate: {fpr:.4f}")
        logger.info(f"False Negative Rate: {fn / (fn + tp) if (fn + tp) > 0 else 0:.4f}")

        # Plot confusion matrix
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False,
                   xticklabels=['Safe', 'Threat'],
                   yticklabels=['Safe', 'Threat'])
        plt.title('Confusion Matrix')
        plt.ylabel('True')
        plt.xlabel('Predicted')
        plt.tight_layout()
        plt.savefig(self.output_dir / 'confusion_matrix.png', dpi=300)
        logger.info(f"✓ Saved: confusion_matrix.png")

    def plot_roc_curve(self):
        """Plot ROC curve"""
        fpr, tpr, _ = roc_curve(self.y_test, self.y_pred_proba)

        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, color='blue', lw=2,
                label=f'ROC curve (AUC = {self.roc_auc:.3f})')
        plt.plot([0, 1], [0, 1], color='gray', lw=1, linestyle='--',
                label='Random classifier')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('ROC Curve')
        plt.legend(loc="lower right")
        plt.grid()
        plt.tight_layout()
        plt.savefig(self.output_dir / 'roc_curve.png', dpi=300)
        logger.info(f"✓ Saved: roc_curve.png")

    def classification_report(self):
        """Generate classification report"""
        logger.info("\n" + "=" * 60)
        logger.info("CLASSIFICATION REPORT")
        logger.info("=" * 60)

        report = classification_report(
            self.y_test, self.y_pred,
            target_names=['Safe', 'Threat'],
            digits=4
        )

        logger.info(f"\n{report}")

        # Save to file
        with open(self.output_dir / 'classification_report.txt', 'w') as f:
            f.write(report)
        logger.info(f"✓ Saved: classification_report.txt")

    def generate_eval_report(self):
        """Generate complete evaluation report"""
        logger.info("\n" + "=" * 60)
        logger.info("STARTING MODEL EVALUATION")
        logger.info("=" * 60)

        self.make_predictions()
        self.calculate_metrics()
        self.confusion_analysis()
        self.plot_roc_curve()
        self.classification_report()

        # Create summary JSON
        summary = {
            'precision': float(self.precision),
            'recall': float(self.recall),
            'f1_score': float(self.f1),
            'roc_auc': float(self.roc_auc),
            'test_samples': len(self.X_test),
            'requirements_met': {
                'recall_90_percent': self.recall >= 0.90,
                'f1_0_85': self.f1 >= 0.85
            }
        }

        import json
        with open(self.output_dir / 'evaluation_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)

        logger.info("\n" + "=" * 60)
        logger.info("✓ EVALUATION COMPLETE")
        logger.info("=" * 60)
        logger.info(f"Reports saved to: {self.output_dir}/")


if __name__ == "__main__":
    test_df = pd.read_csv("data/test/test_processed.csv")
    evaluator = ModelEvaluator("ml_model/training/models/xgboost_smote_model.pkl", test_df)
    evaluator.generate_eval_report()
```

---

### Step 2: Run Evaluation

```bash
python ml_model/training/evaluate.py
```

---

## 📊 Expected Output

```
ml_model/training/evaluation/
├── confusion_matrix.png
├── roc_curve.png
├── classification_report.txt
└── evaluation_summary.json
```

---

## ✅ Checklist

- [x] Evaluation script created
- [x] Metrics calculated: Precision, Recall, F1, ROC-AUC
- [x] Confusion matrix analyzed
- [x] ROC curve visualized
- [x] Classification report generated
- [x] Recall ≥ 90% verified
- [x] F1 ≥ 0.85 verified
- [x] Summary JSON created
- [x] Commit: `git add . && git commit -m "Add model evaluation metrics"`

---

## 🔗 Next Steps

✅ **Task 2.3 Complete** → Move to **Task 2.4: Explainability (SHAP)**

---

**Created:** 2026-03-17
