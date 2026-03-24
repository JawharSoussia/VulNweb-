# Task 2.5: Model Serialization & Packaging

**Phase:** ML Model Development
**Deadline:** Day 25
**Status:** ⏳ Pending
**Dependencies:** Task 2.4 complete

---

## 📋 Objective
Package trained model with metadata, versioning, and create model loader utility for API inference.

---

## 🎯 What to Do

### Step 1: Create Model Package Structure

```bash
# Create model package directory
mkdir -p ml_model/inference/models
mkdir -p ml_model/inference/utils
```

**Create: `ml_model/inference/model_loader.py`**

```python
"""Model Loading and Inference Utility"""
import pickle
import json
import logging
from pathlib import Path
from typing import Dict, Any, Tuple
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelPackage:
    """Manages model loading and versioning"""

    def __init__(self, model_dir: str = "ml_model/inference/models"):
        """Initialize model package"""
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)

        self.model = None
        self.preprocessor = None
        self.explainer = None
        self.metadata = None
        self.feature_names = None

    def load_model(self, model_name: str = "xgboost_smote_model.pkl"):
        """Load trained model"""
        model_path = self.model_dir / model_name

        if not model_path.exists():
            logger.error(f"Model not found: {model_path}")
            raise FileNotFoundError(f"Model not found: {model_path}")

        logger.info(f"Loading model from: {model_path}")
        with open(model_path, 'rb') as f:
            self.model = pickle.load(f)

        logger.info("✓ Model loaded successfully")
        return self.model

    def load_preprocessor(self, preprocessor_name: str = "preprocessor.pkl"):
        """Load preprocessor (scaler, encoder, etc.)"""
        preprocessor_path = Path("ml_model/training") / preprocessor_name

        if not preprocessor_path.exists():
            logger.warning(f"Preprocessor not found: {preprocessor_path}")
            return None

        logger.info(f"Loading preprocessor from: {preprocessor_path}")
        with open(preprocessor_path, 'rb') as f:
            self.preprocessor = pickle.load(f)

        logger.info("✓ Preprocessor loaded")
        return self.preprocessor

    def load_explainer(self, explainer_name: str = "shap_explainer.pkl"):
        """Load SHAP explainer"""
        explainer_path = Path("ml_model/inference") / explainer_name

        if not explainer_path.exists():
            logger.warning(f"Explainer not found: {explainer_path}")
            return None

        logger.info(f"Loading explainer from: {explainer_path}")
        with open(explainer_path, 'rb') as f:
            self.explainer = pickle.load(f)

        logger.info("✓ Explainer loaded")
        return self.explainer

    def load_metadata(self, metadata_name: str = "model_metadata.json"):
        """Load model metadata"""
        metadata_path = Path("ml_model/training/models") / metadata_name

        if not metadata_path.exists():
            logger.warning(f"Metadata not found: {metadata_path}")
            return None

        logger.info(f"Loading metadata from: {metadata_path}")
        with open(metadata_path, 'r') as f:
            self.metadata = json.load(f)

        self.feature_names = self.metadata.get('feature_names', [])
        logger.info(f"✓ Metadata loaded (Version: {self.metadata.get('model_name')})")
        return self.metadata

    def predict(self, X: np.ndarray) -> Dict[str, Any]:
        """Make prediction"""
        if self.model is None:
            raise ValueError("Model not loaded. Call load_model() first.")

        # Make prediction
        pred = self.model.predict(X)
        pred_proba = self.model.predict_proba(X)

        # Threat score 0-100
        threat_score = float(pred_proba[0, 1] * 100)

        # Threat level
        if threat_score >= 70:
            threat_level = "critical"
        elif threat_score >= 30:
            threat_level = "suspicious"
        else:
            threat_level = "safe"

        return {
            'prediction': int(pred[0]),
            'threat_score': threat_score,
            'confidence': float(pred_proba[0, 1]),
            'threat_level': threat_level
        }

    def explain(self, X: np.ndarray, k: int = 3) -> list:
        """Get explanation"""
        if self.explainer is None:
            logger.warning("Explainer not loaded")
            return []

        # Get explanations (simplified)
        return self.explainer.batch_explain(X, k=k)

    def load_all(self):
        """Load all components"""
        logger.info("\n" + "=" * 60)
        logger.info("LOADING MODEL PACKAGE")
        logger.info("=" * 60)

        self.load_model()
        self.load_preprocessor()
        self.load_metadata()
        self.load_explainer()

        logger.info("\n✓ All components loaded successfully")
        return self


if __name__ == "__main__":
    # Test loading
    package = ModelPackage()
    package.load_all()

    # Verify
    print(f"Model: {package.model}")
    print(f"Metadata: {package.metadata}")
```

---

### Step 2: Create Model Version Management

**Create: `ml_model/inference/version_manager.py`**

```python
"""Model Versioning and Registry"""
import json
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelVersionManager:
    """Manage model versions"""

    def __init__(self, registry_file: str = "ml_model/inference/model_registry.json"):
        self.registry_file = Path(registry_file)
        self.registry = self._load_registry()

    def _load_registry(self) -> dict:
        """Load version registry"""
        if self.registry_file.exists():
            with open(self.registry_file, 'r') as f:
                return json.load(f)
        return {'versions': []}

    def register_model(self, model_name: str, model_version: str, metadata: dict):
        """Register new model version"""
        entry = {
            'model_name': model_name,
            'version': model_version,
            'timestamp': datetime.now().isoformat(),
            'metrics': metadata.get('cv_results', {}),
            'status': 'active'
        }

        self.registry['versions'].append(entry)
        self._save_registry()
        logger.info(f"✓ Registered: {model_name} v{model_version}")

    def _save_registry(self):
        """Save registry to disk"""
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.registry_file, 'w') as f:
            json.dump(self.registry, f, indent=2)

    def get_latest_version(self) -> dict:
        """Get latest model version"""
        if self.registry['versions']:
            return self.registry['versions'][-1]
        return None

    def list_versions(self):
        """List all registered versions"""
        for entry in self.registry['versions']:
            logger.info(f"  {entry['model_name']} v{entry['version']} ({entry['timestamp']})")
```

---

### Step 3: Create Inference Serving Module

**Create: `ml_model/inference/predictor.py`**

```python
"""High-level prediction interface"""
import numpy as np
import pandas as pd
from model_loader import ModelPackage
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Predictor:
    """High-level prediction interface"""

    def __init__(self):
        """Initialize predictor"""
        self.package = ModelPackage()
        self.package.load_all()

    def predict_batch(self, feature_list: list) -> list:
        """Predict on batch of feature vectors"""
        X = np.array(feature_list).reshape(len(feature_list), -1)
        results = []

        for i in range(len(X)):
            pred = self.package.predict(X[i:i+1])
            exp = self.package.explain(X[i:i+1])
            results.append({
                **pred,
                'explanation': exp[0] if exp else []
            })

        return results

    def predict_single(self, features: dict) -> dict:
        """Predict on single sample"""
        # Convert features to array in correct order
        feature_array = np.array([
            features.get(fname, 0) for fname in self.package.feature_names
        ]).reshape(1, -1)

        result = self.package.predict(feature_array)
        explanation = self.package.explain(feature_array)

        return {
            **result,
            'explanation': explanation[0] if explanation else []
        }


if __name__ == "__main__":
    predictor = Predictor()

    # Test prediction
    sample_features = {fname: np.random.randn() for fname in predictor.package.feature_names}
    result = predictor.predict_single(sample_features)

    print(f"Prediction: {result}")
```

---

### Step 4: Package Everything

```bash
# Create package info file
cat > ml_model/inference/__init__.py << 'EOF'
"""ML Model Inference Package"""
from .model_loader import ModelPackage
from .predictor import Predictor

__version__ = "1.0.0"
EOF

# Verify all files exist
ls -la ml_model/inference/
```

---

### Step 5: Verify Model Package

```bash
# Test loading
python << 'EOF'
from ml_model.inference import ModelPackage

package = ModelPackage()
package.load_all()
print("✓ Model package loaded successfully")
print(f"Model version: {package.metadata.get('model_name')}")
print(f"Features: {len(package.feature_names)}")
EOF
```

---

## 📊 Expected Structure

```
ml_model/inference/
├── __init__.py
├── model_loader.py
├── predictor.py
├── version_manager.py
├── explainer.py
├── model_registry.json
└── models/
    └── xgboost_smote_model.pkl
```

---

## ✅ Checklist

- [x] Model loader utility created
- [x] Metadata management implemented
- [x] Version management system created
- [x] High-level predictor interface built
- [x] Model package verified and loaded
- [x] All components packaged
- [x] Commit: `git add . && git commit -m "Add model serialization and packaging"`

---

## 🔗 Next Steps

✅ **Phase 2 Complete** → Move to **Phase 3: Backend API Development**

✅ **Task 2.5 Complete** → Move to **Task 3.1: FastAPI Setup**

---

**Created:** 2026-03-17
