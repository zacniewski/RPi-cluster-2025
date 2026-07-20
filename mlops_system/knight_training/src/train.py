"""
train.py — Model training script for knight-cluster.

Loads the processed dataset, trains a scikit-learn model, evaluates it,
logs metrics to MLflow, and exports the model artifact.

Usage:
    python src/train.py                          # use config defaults
    python src/train.py --model random_forest    # override model type
    python src/train.py --push                   # push model to rook after training
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import mlflow
import pandas as pd
import yaml
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

from evaluate import evaluate_model

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("train")

CONFIG_PATH = Path("/app/config/training_config.yaml")

MODEL_REGISTRY = {
    "random_forest": RandomForestClassifier,
    "gradient_boosting": GradientBoostingClassifier,
    "logistic_regression": LogisticRegression,
}


def load_config() -> dict:
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


def load_dataset(cfg: dict) -> tuple[pd.DataFrame, pd.Series]:
    """Load dataset and split into features and target."""
    df = pd.read_csv(cfg["dataset_path"])
    logger.info("Loaded dataset: %d rows, %d columns", len(df), len(df.columns))

    target_col = cfg["target_column"]
    feature_cols = cfg.get("feature_columns") or [c for c in df.columns if c != target_col]

    X = df[feature_cols]
    y = df[target_col]
    return X, y


def build_model(cfg: dict):
    """Instantiate the model with hyperparameters from config."""
    model_type = cfg["model_type"]
    if model_type not in MODEL_REGISTRY:
        raise ValueError(f"Unknown model_type: {model_type}. Choose from {list(MODEL_REGISTRY)}")

    params = cfg["hyperparameters"].get(model_type, {})
    model_cls = MODEL_REGISTRY[model_type]
    model = model_cls(**params)
    logger.info("Built model: %s with params %s", model_type, params)
    return model, params


def save_model(model, model_dir: Path, ts: str, fmt: str) -> Path:
    """Save the trained model to disk."""
    model_dir.mkdir(parents=True, exist_ok=True)
    ext = "joblib" if fmt == "joblib" else "pkl"
    path = model_dir / f"model_{ts}.{ext}"

    if fmt == "joblib":
        joblib.dump(model, path)
    else:
        import pickle
        with open(path, "wb") as f:
            pickle.dump(model, f)

    # Update latest symlink
    latest = model_dir / f"latest.{ext}"
    latest.unlink(missing_ok=True)
    latest.symlink_to(path.name)
    logger.info("Saved model to %s", path)
    return path


def save_log(log_dir: Path, ts: str, status: str, details: dict) -> None:
    log_dir.mkdir(parents=True, exist_ok=True)
    entry = {"timestamp": ts, "status": status, **details}
    log_path = log_dir / "training_log.jsonl"
    with open(log_path, "a") as f:
        f.write(json.dumps(entry) + "\n")


def run(model_override: str | None = None, push: bool = False) -> dict:
    """Execute the full training pipeline."""
    cfg = load_config()
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    if model_override:
        cfg["model_type"] = model_override

    model_dir = Path(cfg["model_dir"])
    log_dir = Path(cfg["log_dir"])

    # 1. Load data
    X, y = load_dataset(cfg)

    # 2. Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=cfg.get("test_size", 0.2),
        random_state=cfg.get("random_state", 42),
    )
    logger.info("Split: train=%d, test=%d", len(X_train), len(X_test))

    # 3. Build and train
    model, params = build_model(cfg)

    # 4. MLflow tracking
    mlflow_uri = cfg.get("mlflow_tracking_uri", "")
    experiment_name = cfg.get("mlflow_experiment_name", "default")

    if mlflow_uri:
        try:
            mlflow.set_tracking_uri(mlflow_uri)
            mlflow.set_experiment(experiment_name)
        except Exception as exc:
            logger.warning("MLflow connection failed (%s), training without tracking.", exc)
            mlflow_uri = ""

    run_context = mlflow.start_run() if mlflow_uri else _null_context()

    with run_context:
        model.fit(X_train, y_train)
        logger.info("Training complete.")

        # 5. Evaluate
        metrics = evaluate_model(model, X_test, y_test)
        logger.info("Metrics: %s", metrics)

        # 6. Log to MLflow
        if mlflow_uri:
            mlflow.log_params(params)
            mlflow.log_param("model_type", cfg["model_type"])
            mlflow.log_param("dataset_rows", len(X))
            mlflow.log_metrics(metrics)

        # 7. Save model
        model_path = save_model(model, model_dir, ts, cfg.get("export_format", "joblib"))

        if mlflow_uri:
            mlflow.log_artifact(str(model_path))

    # 8. Push to rook
    if push:
        try:
            from export_model import push_to_rook
            push_to_rook(model_path, cfg)
        except Exception as exc:
            logger.error("Push to rook-cluster failed: %s", exc)
            save_log(log_dir, ts, "PUSH_FAILED", {"error": str(exc), **metrics})
            return {"status": "push_failed", "timestamp": ts, **metrics}

    save_log(log_dir, ts, "SUCCESS", metrics)
    return {"status": "success", "timestamp": ts, "model_path": str(model_path), **metrics}


class _null_context:
    """No-op context manager when MLflow is unavailable."""
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass


def main() -> None:
    parser = argparse.ArgumentParser(description="Run model training pipeline")
    parser.add_argument("--model", type=str, default=None, help="Override model_type")
    parser.add_argument("--push", action="store_true", help="Push model to rook-cluster")
    args = parser.parse_args()

    result = run(model_override=args.model, push=args.push)
    logger.info("Training result: %s", json.dumps(result, indent=2))
    if result["status"] != "success":
        sys.exit(1)


if __name__ == "__main__":
    main()
