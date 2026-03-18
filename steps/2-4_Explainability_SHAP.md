# Task 2.4: Explainability with SHAP

**Phase:** ML Model Development
**Deadline:** Day 24
**Status:** ⏳ Pending
**Dependencies:** Task 2.3 complete

---

## 📋 Objective
Implement SHAP (SHapley Additive exPlanations) for model interpretability. Extract top 3 decision reasons per prediction.

---

## 🎯 What to Do

### Step 1: Create SHAP Explainability Module

**Create: `ml_model/inference/explainer.py`**

```python
"""SHAP-based Model Explainability"""
import pandas as pd
import numpy as np
import pickle
import shap
import logging
from pathlib import Path
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelExplainer:
    """Extract SHAP-based explanations"""

    def __init__(self, model_path, train_df, feature_names: List[str]):
        """Initialize explainer"""
        with open(model_path, 'rb') as f:
            self.model = pickle.load(f)

        # Use sample of training data as background
        self.background_data = train_df.iloc[:min(100, len(train_df))]
        self.feature_names = feature_names

        logger.info(f"Initializing SHAP explainer with {len(self.background_data)} background samples")
        self.explainer = None

    def initialize_explainer(self, explainer_type='tree'):
        """Initialize SHAP explainer"""
        logger.info("Creating SHAP explainer...")

        if explainer_type == 'tree':
            # For tree-based models (XGBoost, RandomForest)
            self.explainer = shap.TreeExplainer(self.model)
        elif explainer_type == 'kernel':
            # For any model (slower but model-agnostic)
            self.explainer = shap.KernelExplainer(
                self.model.predict_proba,
                shap.sample(self.background_data, 50)
            )

        logger.info(f"✓ {explainer_type} explainer initialized")

    def get_top_k_explanations(self, X_sample: pd.DataFrame, k: int = 3) -> Dict:
        """Get top k feature explanations for a single sample"""

        # Calculate SHAP values
        shap_values = self.explainer.shap_values(X_sample)

        # Handle multi-class output
        if isinstance(shap_values, list):
            shap_values = shap_values[1]  # Get SHAP values for threat class

        # Get absolute importance
        feature_importance = np.abs(shap_values[0]).flatten()

        # Get top k features
        top_indices = np.argsort(feature_importance)[-k:][::-1]

        explanations = []
        for idx in top_indices:
            feature_name = self.feature_names[idx]
            importance = float(feature_importance[idx])
            value = float(X_sample.iloc[0, idx])

            explanations.append({
                'feature': feature_name,
                'importance': importance,
                'value': value
            })

        return explanations

    def format_explanation(self, explanation: Dict) -> str:
        """Format explanation for display"""
        feature = explanation['feature']
        importance = explanation['importance']
        value = explanation['value']

        return f"{feature} ({value:.2f}): {importance:.4f}"

    def batch_explain(self, X: pd.DataFrame, k: int = 3) -> List[List[str]]:
        """Generate explanations for batch of samples"""
        logger.info(f"Generating explanations for {len(X)} samples...")

        all_explanations = []
        for idx, row in X.iterrows():
            sample_df = X.iloc[[idx]]
            explanations = self.get_top_k_explanations(sample_df, k)
            formatted = [self.format_explanation(exp) for exp in explanations]
            all_explanations.append(formatted)

        return all_explanations

    def visualize_sample_explanation(self, X_sample: pd.DataFrame, output_path: str = None):
        """Create visualization of explanation"""
        shap_values = self.explainer.shap_values(X_sample)

        if isinstance(shap_values, list):
            shap_values = shap_values[1]

        # Force plot
        shap.force_plot(
            self.explainer.expected_value[1],
            shap_values[0],
            X_sample.iloc[0],
            feature_names=self.feature_names,
            matplotlib=True,
            show=False
        )

        if output_path:
            import matplotlib.pyplot as plt
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            logger.info(f"✓ Saved explanation plot: {output_path}")


if __name__ == "__main__":
    # Load model and data
    model_path = "ml_model/training/models/xgboost_smote_model.pkl"
    train_df = pd.read_csv("data/train/train_processed.csv")
    test_df = pd.read_csv("data/test/test_processed.csv")

    # Get feature names
    feature_names = [col for col in train_df.columns if col != 'label']

    # Initialize explainer
    X_train = train_df.drop(columns=['label'])
    explainer = ModelExplainer(model_path, X_train, feature_names)
    explainer.initialize_explainer(explainer_type='tree')

    # Test on first 5 samples
    X_test = test_df.drop(columns=['label'])
    explanations = explainer.batch_explain(X_test.head(5), k=3)

    print("\nSample Explanations:")
    for idx, exp_list in enumerate(explanations):
        print(f"\nSample {idx + 1}:")
        for exp in exp_list:
            print(f"  - {exp}")

    # Save explainer
    Path("ml_model/inference").mkdir(exist_ok=True)
    with open("ml_model/inference/shap_explainer.pkl", 'wb') as f:
        pickle.dump(explainer, f)

    logger.info("✓ Explainer saved!")
```

---

### Step 2: Install SHAP

```bash
pip install shap
echo "shap==0.43.0" >> requirements.txt
```

---

### Step 3: Run Explainer

```bash
python ml_model/inference/explainer.py
```

---

## ✅ Checklist

- [ ] SHAP explainer created
- [ ] TreeExplainer initialized
- [ ] Top-3 explanation extraction working
- [ ] Batch explanation generation implemented
- [ ] Visualization functions created
- [ ] Explainer object saved
- [ ] Tested on sample predictions
- [ ] Commit: `git add . && git commit -m "Add SHAP model explainability"`

---

## 🔗 Next Steps

✅ **Task 2.4 Complete** → Move to **Task 2.5: Model Serialization & Packaging**

---

**Created:** 2026-03-17
