"""
api.py — FastAPI status and trigger API for knight-cluster.

Endpoints:
    GET  /health    — liveness check and last training status
    POST /train     — trigger a training run
"""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel

from train import run as run_training

app = FastAPI(
    title="Knight Training API",
    description="Model training service on knight-cluster",
    version="1.0.0",
)

LOG_PATH = Path("/logs/training_log.jsonl")


class TrainRequest(BaseModel):
    model_type: str | None = None
    push: bool = False


class TrainResponse(BaseModel):
    status: str
    timestamp: str | None = None
    model_path: str | None = None
    accuracy: float | None = None
    f1_weighted: float | None = None
    precision_weighted: float | None = None
    recall_weighted: float | None = None


def _last_log_entry() -> dict | None:
    if not LOG_PATH.exists():
        return None
    lines = LOG_PATH.read_text().strip().splitlines()
    if not lines:
        return None
    return json.loads(lines[-1])


@app.get("/health")
def health():
    last = _last_log_entry()
    return {
        "service": "knight-training",
        "status": "healthy",
        "last_training": last,
    }


@app.post("/train", response_model=TrainResponse)
def trigger_train(req: TrainRequest):
    """Trigger a training run. Runs synchronously."""
    result = run_training(model_override=req.model_type, push=req.push)
    return TrainResponse(**{k: v for k, v in result.items() if k in TrainResponse.model_fields})
