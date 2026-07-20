"""
model_loader.py — Model loading and hot-reload for rook-cluster.

Watches the models directory for new artifacts and reloads automatically.
Thread-safe: the model reference is swapped atomically.
"""

from __future__ import annotations

import logging
import os
import threading
import time
from pathlib import Path

import joblib

logger = logging.getLogger("model_loader")

# Iris class labels for the demo — update when switching datasets
CLASS_LABELS = {0: "setosa", 1: "versicolor", 2: "virginica"}


class ModelManager:
    """Loads and serves a scikit-learn model from disk with hot-reload."""

    def __init__(self, model_dir: str = "/models"):
        self.model_dir = Path(model_dir)
        self._model = None
        self._model_version: str | None = None
        self._lock = threading.Lock()
        self._watcher_thread: threading.Thread | None = None
        self._stop_event = threading.Event()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    @property
    def model(self):
        return self._model

    @property
    def model_version(self) -> str | None:
        return self._model_version

    @property
    def is_loaded(self) -> bool:
        return self._model is not None

    def load(self) -> bool:
        """Load the latest model from disk. Returns True on success."""
        path = self._find_latest()
        if path is None:
            logger.warning("No model file found in %s", self.model_dir)
            return False
        return self._load_from(path)

    def predict(self, features: list[list[float]]) -> list[dict]:
        """Run prediction on a list of feature vectors."""
        if not self.is_loaded:
            raise RuntimeError("No model loaded")

        import numpy as np
        X = np.array(features)
        predictions = self._model.predict(X)

        # Try to get probabilities
        probas = None
        if hasattr(self._model, "predict_proba"):
            try:
                probas = self._model.predict_proba(X)
            except Exception:
                pass

        results = []
        for i, pred in enumerate(predictions):
            pred_int = int(pred)
            result = {
                "prediction": pred_int,
                "label": CLASS_LABELS.get(pred_int, f"class_{pred_int}"),
                "model_version": self._model_version or "unknown",
            }
            if probas is not None:
                result["confidence"] = round(float(probas[i].max()), 4)
            else:
                result["confidence"] = None
            results.append(result)
        return results

    # ------------------------------------------------------------------
    # Hot-reload watcher
    # ------------------------------------------------------------------

    def start_watcher(self, interval: int = 10) -> None:
        """Start a background thread that checks for new model files."""
        if self._watcher_thread is not None:
            return
        self._stop_event.clear()
        self._watcher_thread = threading.Thread(
            target=self._watch_loop, args=(interval,), daemon=True,
        )
        self._watcher_thread.start()
        logger.info("Model watcher started (interval=%ds)", interval)

    def stop_watcher(self) -> None:
        self._stop_event.set()
        if self._watcher_thread:
            self._watcher_thread.join(timeout=5)
            self._watcher_thread = None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _find_latest(self) -> Path | None:
        """Find the latest model file (prefers 'latest.*' symlink)."""
        for ext in ("joblib", "pkl"):
            latest = self.model_dir / f"latest.{ext}"
            if latest.exists():
                return latest
        # Fallback: newest file by mtime
        candidates = list(self.model_dir.glob("model_*.*"))
        if not candidates:
            return None
        return max(candidates, key=lambda p: p.stat().st_mtime)

    def _load_from(self, path: Path) -> bool:
        try:
            model = joblib.load(path)
            with self._lock:
                self._model = model
                self._model_version = path.name
            logger.info("Loaded model: %s", path.name)
            return True
        except Exception as exc:
            logger.error("Failed to load model from %s: %s", path, exc)
            return False

    def _watch_loop(self, interval: int) -> None:
        last_mtime: float | None = None
        while not self._stop_event.is_set():
            path = self._find_latest()
            if path is not None:
                try:
                    # Resolve symlink to get actual file mtime
                    real_path = path.resolve()
                    mtime = real_path.stat().st_mtime
                    if last_mtime is None or mtime > last_mtime:
                        self._load_from(path)
                        last_mtime = mtime
                except Exception as exc:
                    logger.error("Watcher error: %s", exc)
            time.sleep(interval)
