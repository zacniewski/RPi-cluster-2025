"""
api.py — FastAPI prediction API for rook-cluster.

Endpoints:
    GET  /health          — liveness check and model status
    POST /predict         — single prediction
    POST /predict/batch   — batch predictions
    POST /reload          — force model reload from disk
"""

from __future__ import annotations

import json
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException

from model_loader import ModelManager
from schemas import (
    BatchPredictRequest,
    BatchPredictResponse,
    HealthResponse,
    PredictRequest,
    PredictResponse,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("serving-api")

MODEL_DIR = "/models"
LOG_DIR = Path("/logs")

manager = ModelManager(model_dir=MODEL_DIR)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model and start watcher on startup; stop watcher on shutdown."""
    manager.load()
    manager.start_watcher(interval=10)
    yield
    manager.stop_watcher()


app = FastAPI(
    title="Rook Model Serving API",
    description="Prediction API on rook-cluster — serves the latest trained model",
    version="1.0.0",
    lifespan=lifespan,
)


def _log_prediction(request_data: dict, response_data: dict) -> None:
    """Append prediction to the log file."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "request": request_data,
        "response": response_data,
    }
    log_path = LOG_DIR / "prediction_log.jsonl"
    with open(log_path, "a") as f:
        f.write(json.dumps(entry) + "\n")


@app.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(
        service="rook-model-serving",
        status="healthy" if manager.is_loaded else "no_model",
        model_loaded=manager.is_loaded,
        model_version=manager.model_version,
    )


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    if not manager.is_loaded:
        raise HTTPException(status_code=503, detail="No model loaded. Deploy a model first.")

    features = [[req.sepal_length, req.sepal_width, req.petal_length, req.petal_width]]
    results = manager.predict(features)
    result = results[0]

    _log_prediction(req.model_dump(), result)
    return PredictResponse(**result)


@app.post("/predict/batch", response_model=BatchPredictResponse)
def predict_batch(req: BatchPredictRequest):
    if not manager.is_loaded:
        raise HTTPException(status_code=503, detail="No model loaded. Deploy a model first.")

    features = [
        [inst.sepal_length, inst.sepal_width, inst.petal_length, inst.petal_width]
        for inst in req.instances
    ]
    results = manager.predict(features)

    _log_prediction(req.model_dump(), {"predictions": results})
    return BatchPredictResponse(predictions=[PredictResponse(**r) for r in results])


@app.post("/reload")
def reload_model():
    """Force reload the model from disk."""
    ok = manager.load()
    if ok:
        return {"status": "reloaded", "model_version": manager.model_version}
    raise HTTPException(status_code=500, detail="Failed to reload model.")
