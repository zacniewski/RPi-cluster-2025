"""
dashboard_api.py — FastAPI dashboard and control API for queen-cluster.

Endpoints:
    GET  /health              — queen-cluster liveness
    GET  /pipeline/status     — last pipeline run status
    POST /pipeline/run        — trigger a pipeline run now
    POST /pipeline/run/{step} — trigger a single step
    POST /scheduler/start     — start the automatic scheduler
    POST /scheduler/stop      — stop the automatic scheduler
    GET  /scheduler/status    — check if the scheduler is running
    GET  /cluster/health      — aggregate health from all nodes
"""

from __future__ import annotations

import json
import logging
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
import yaml
from fastapi import FastAPI

from pipeline_runner import run_pipeline
from scheduler import is_running, start_scheduler, stop_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("dashboard")

CONFIG_PATH = Path("/app/config/pipeline_config.yaml")
LOG_PATH = Path("/logs/pipeline_log.jsonl")


def _load_config() -> dict:
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Optionally start the scheduler on boot."""
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(
    title="Queen Orchestration Dashboard",
    description="MLOps pipeline control and monitoring on queen-cluster",
    version="1.0.0",
    lifespan=lifespan,
)


def _last_pipeline_log() -> dict | None:
    if not LOG_PATH.exists():
        return None
    lines = LOG_PATH.read_text().strip().splitlines()
    if not lines:
        return None
    return json.loads(lines[-1])


@app.get("/health")
def health():
    return {
        "service": "queen-orchestration",
        "status": "healthy",
        "scheduler_running": is_running(),
    }


@app.get("/pipeline/status")
def pipeline_status():
    last = _last_pipeline_log()
    return {"last_run": last}


@app.post("/pipeline/run")
def trigger_pipeline():
    """Trigger a full pipeline run (synchronous)."""
    result = run_pipeline()
    return result


@app.post("/pipeline/run/{step_name}")
def trigger_step(step_name: str):
    """Trigger a single pipeline step."""
    result = run_pipeline(step_filter=step_name)
    return result


@app.post("/scheduler/start")
def api_start_scheduler():
    start_scheduler()
    return {"status": "scheduler_started", "running": is_running()}


@app.post("/scheduler/stop")
def api_stop_scheduler():
    stop_scheduler()
    return {"status": "scheduler_stopped", "running": is_running()}


@app.get("/scheduler/status")
def scheduler_status():
    return {"running": is_running()}


@app.get("/cluster/health")
async def cluster_health():
    """Aggregate health status from all nodes."""
    cfg = _load_config()
    nodes = cfg["nodes"]
    results = {}

    async with httpx.AsyncClient(timeout=5) as client:
        for name, node_cfg in nodes.items():
            url = f"http://{node_cfg['host']}:{node_cfg['api_port']}/health"
            try:
                resp = await client.get(url)
                results[name] = {"status": "reachable", "response": resp.json()}
            except Exception as exc:
                results[name] = {"status": "unreachable", "error": str(exc)}

    return {"nodes": results}
