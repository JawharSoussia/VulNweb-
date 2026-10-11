"""Train the optional PyTorch URL-threat classifier.

This complements the existing XGBoost training pipeline. It intentionally
uses the same processed CSV files and feature order so either backend can be
selected by the API.
"""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score
from sklearn.preprocessing import StandardScaler

from ml_model.inference.pytorch_model import build_model, predict_proba


def train(
    train_path: Path,
    test_path: Path,
    output_dir: Path,
    epochs: int = 30,
    batch_size: int = 512,
    seed: int = 42,
) -> None:
    try:
        import torch
        from torch.utils.data import DataLoader, TensorDataset
    except ImportError as exc:
        raise RuntimeError(
            "PyTorch is required to train this model. Install it with: pip install torch"
        ) from exc

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)

    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)
    target_col = "threat_level"
    feature_names = [column for column in train_df.columns if column != target_col]

    scaler = StandardScaler()
    X_train = scaler.fit_transform(train_df[feature_names].to_numpy(dtype=np.float32))
    X_test = scaler.transform(test_df[feature_names].to_numpy(dtype=np.float32))
    y_train = train_df[target_col].to_numpy(dtype=np.int64)
    y_test = test_df[target_col].to_numpy(dtype=np.int64)

    model = build_model(len(feature_names), 3)
    class_counts = np.bincount(y_train, minlength=3)
    class_weights = len(y_train) / (3 * np.maximum(class_counts, 1))
    loss_fn = torch.nn.CrossEntropyLoss(
        weight=torch.tensor(class_weights, dtype=torch.float32)
    )
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    dataset = TensorDataset(
        torch.tensor(X_train, dtype=torch.float32),
        torch.tensor(y_train, dtype=torch.long),
    )
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    for epoch in range(epochs):
        model.train()
        for features, labels in loader:
            optimizer.zero_grad()
            loss = loss_fn(model(features), labels)
            loss.backward()
            optimizer.step()

        if (epoch + 1) % 5 == 0 or epoch == 0:
            probabilities = predict_proba(model, X_test)
            predictions = probabilities.argmax(axis=1)
            print(
                f"epoch={epoch + 1:02d}/{epochs} "
                f"accuracy={accuracy_score(y_test, predictions):.4f} "
                f"f1_macro={f1_score(y_test, predictions, average='macro'):.4f}"
            )

    output_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_path = output_dir / "pytorch_url_threat.pt"
    metadata_path = output_dir / "pytorch_url_threat_metadata.json"
    torch.save(
        {
            "state_dict": model.state_dict(),
            "input_features": len(feature_names),
            "num_classes": 3,
            "scaler_mean": scaler.mean_.tolist(),
            "scaler_scale": scaler.scale_.tolist(),
        },
        checkpoint_path,
    )
    metadata_path.write_text(
        json.dumps(
            {
                "model_name": "PyTorch URL Threat MLP",
                "model_backend": "pytorch",
                "feature_names": feature_names,
                "num_classes": 3,
                "target_col": target_col,
                "checkpoint": checkpoint_path.name,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Saved checkpoint: {checkpoint_path}")
    print(f"Saved metadata: {metadata_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", default="data/train/train_processed.csv")
    parser.add_argument("--test", default="data/test/test_processed.csv")
    parser.add_argument("--output-dir", default="ml_model/inference/models")
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--batch-size", type=int, default=512)
    args = parser.parse_args()
    train(
        Path(args.train),
        Path(args.test),
        Path(args.output_dir),
        epochs=args.epochs,
        batch_size=args.batch_size,
    )


if __name__ == "__main__":
    main()
