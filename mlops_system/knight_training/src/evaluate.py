"""
evaluate.py — Model evaluation utilities for knight-cluster.

Computes classification metrics on a held-out test set and returns them
as a flat dict suitable for MLflow logging.
"""

from __future__ import annotations

from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
)


def evaluate_model(model, X_test, y_test) -> dict[str, float]:
    """Run predictions on the test set and return a metrics dict."""
    y_pred = model.predict(X_test)

    metrics = {
        "accuracy": round(accuracy_score(y_test, y_pred), 4),
        "f1_weighted": round(f1_score(y_test, y_pred, average="weighted", zero_division=0), 4),
        "precision_weighted": round(precision_score(y_test, y_pred, average="weighted", zero_division=0), 4),
        "recall_weighted": round(recall_score(y_test, y_pred, average="weighted", zero_division=0), 4),
    }
    return metrics
