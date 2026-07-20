"""
api.py — FastAPI status and trigger API for pawn-cluster.

Endpoints:
    GET  /health         — liveness check and last ingestion status
    POST /ingest         — trigger an ingestion run
    GET  /data/status    — details about the latest processed dataset
"""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel

from ingest import run as run_ingestion

app = FastAPI(
    title="Pawn Data Ingestion API",
    description="Data ingestion and validation service on pawn-cluster",
    version="1.0.0",
)

LOG_PATH = Path("/data/logs/ingestion_log.jsonl")
PROCESSED_DIR = Path("/data/processed")


class IngestRequest(BaseModel):
    source: str | None = None
    push: bool = False


class IngestResponse(BaseModel):
    status: str
    timestamp: str | None = None
    rows: int | None = None
    columns: int | None = None
    report: str | None = None


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
        "service": "pawn-data-ingestion",
        "status": "healthy",
        "last_ingestion": last,
    }


@app.get("/data/status")
def data_status():
    latest = PROCESSED_DIR / "latest.csv"
    if latest.exists():
        import os
        stat = os.stat(latest)
        # Count lines (rows) quickly
        with open(latest) as f:
            row_count = sum(1 for _ in f) - 1  # subtract header
        return {
            "latest_file": str(latest.resolve()),
            "size_bytes": stat.st_size,
            "rows": row_count,
            "ready": True,
        }
    return {"ready": False, "message": "No processed dataset available yet."}


@app.post("/ingest", response_model=IngestResponse)
def trigger_ingest(req: IngestRequest, background_tasks: BackgroundTasks):
    """Trigger an ingestion run. Runs synchronously for simplicity."""
    result = run_ingestion(source_override=req.source, push=req.push)
    return IngestResponse(**result)
