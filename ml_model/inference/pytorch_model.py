"""PyTorch model used by the optional URL-threat inference backend."""
from __future__ import annotations

from typing import Any

import numpy as np


def build_model(input_features: int, num_classes: int = 3) -> Any:
    """Create the small MLP used for tabular URL features.

    The import is intentionally lazy so the existing XGBoost backend does not
    require PyTorch at runtime.
    """
    try:
        import torch.nn as nn
    except ImportError as exc:
        raise RuntimeError(
            "PyTorch is required when VULNWEB_MODEL_BACKEND=pytorch. "
            "Install it with: pip install torch"
        ) from exc

    return nn.Sequential(
        nn.Linear(input_features, 64),
        nn.ReLU(),
        nn.Dropout(0.2),
        nn.Linear(64, 32),
        nn.ReLU(),
        nn.Linear(32, num_classes),
    )


def predict_proba(model: Any, features: np.ndarray) -> np.ndarray:
    """Return class probabilities for a batch of feature vectors."""
    try:
        import torch
    except ImportError as exc:
        raise RuntimeError(
            "PyTorch is required when VULNWEB_MODEL_BACKEND=pytorch. "
            "Install it with: pip install torch"
        ) from exc

    model.eval()
    with torch.no_grad():
        logits = model(torch.as_tensor(features, dtype=torch.float32))
        return torch.softmax(logits, dim=1).cpu().numpy()
