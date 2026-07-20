# Queen-Cluster — Orchestration and Tracking Node

Detailed documentation for the orchestration, scheduling, and experiment tracking services running on `queen-cluster`.

## Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Directory Layout](#directory-layout)
- [MLflow Tracking Server](#mlflow-tracking-server)
- [Pipeline Runner](#pipeline-runner)
- [Scheduler](#scheduler)
- [API Reference](#api-reference)
- [Configuration](#configuration)
- [Docker Details](#docker-details)

---

## Overview

The queen node is the **control centre** of the MLOps system. It runs two containers:

1. **MLflow server** — stores experiment runs, parameters, metrics, and model artifacts from knight-cluster
2. **Orchestrator** — schedules and triggers the end-to-end pipeline, provides a dashboard API, and aggregates cluster health

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                      queen-cluster                        │
│                                                           │
│  ┌─────────────────────┐    ┌──────────────────────────┐ │
│  │  MLflow Server       │    │  Orchestrator (FastAPI)   │ │
│  │  Port 5000           │    │  Port 8083                │ │
│  │                      │    │                           │ │
│  │  - Experiment UI     │    │  - Pipeline runner        │ │
│  │  - Metric storage    │    │  - APScheduler            │ │
│  │  - Artifact store    │    │  - Cluster health agg.    │ │
│  │  - SQLite backend    │    │  - Pipeline status logs   │ │
│  └─────────────────────┘    └──────────────────────────┘ │
│                                                           │
│  Triggers:  pawn (ingest) → knight (train) → rook (reload)│
└──────────────────────────────────────────────────────────┘
```

## Directory Layout

```
/home/artur/ORCHESTRATION/
├── mlflow/                 # MLflow data (persistent)
│   ├── mlflow.db           # SQLite backend store
│   └── artifacts/          # Model artifacts logged by knight
├── logs/                   # Pipeline run logs
│   └── pipeline_log.jsonl
└── app/                    # Application code
    ├── Dockerfile
    ├── docker-compose.yml
    ├── src/
    └── config/
```

## MLflow Tracking Server

The MLflow server runs as a Docker container and provides:

- **Web UI** at `http://queen-cluster:5000` — browse experiments, compare runs, view metrics
- **REST API** — used by knight-cluster's training script to log parameters, metrics, and artifacts
- **SQLite backend** — all data stored in `/home/artur/ORCHESTRATION/mlflow/mlflow.db`
- **Local artifact store** — model files stored in `/home/artur/ORCHESTRATION/mlflow/artifacts/`

### Accessing MLflow

Open `http://queen-cluster:5000` in your browser. You will see:

- **Experiments** — each training run grouped by experiment name
- **Runs** — individual training runs with parameters, metrics, and artifacts
- **Compare** — side-by-side comparison of multiple runs
- **Artifacts** — download trained model files

### MLflow Configuration

The knight-cluster training script connects to MLflow using:

```bash
MLFLOW_TRACKING_URI=http://queen-cluster:5000
```

This is set in the knight's `docker-compose.yml` and `training_config.yaml`.

## Pipeline Runner

The pipeline runner (`src/pipeline_runner.py`) executes the full MLOps pipeline by calling HTTP endpoints on each node in sequence:

1. **Ingest** — `POST http://pawn-cluster:8081/ingest` (with `push: true`)
2. **Train** — `POST http://knight-cluster:8082/train` (with `push: true`)
3. **Reload** — `POST http://rook-cluster:8080/reload`

If any step fails, the pipeline stops and logs the failure.

### Running Manually

```bash
# Full pipeline
docker compose exec orchestrator python src/pipeline_runner.py

# Single step
docker compose exec orchestrator python src/pipeline_runner.py --step ingest
docker compose exec orchestrator python src/pipeline_runner.py --step train
docker compose exec orchestrator python src/pipeline_runner.py --step reload_model
```

## Scheduler

The scheduler (`src/scheduler.py`) uses APScheduler to run the pipeline automatically on a configurable interval.

- **Default interval:** every 6 hours
- **Starts automatically** when the orchestrator container boots
- **Can be stopped/started** via the API

The interval is configured in `config/pipeline_config.yaml`:

```yaml
schedule_interval_hours: 6
```

## API Reference

Base URL: `http://queen-cluster:8083`

Interactive docs: `http://queen-cluster:8083/docs`

### `GET /health`
Queen-cluster liveness and scheduler status.

### `GET /pipeline/status`
Returns the last pipeline run result.

### `POST /pipeline/run`
Trigger a full pipeline run (synchronous — waits for completion).

**Response:**
```json
{
  "status": "success",
  "timestamp": "20250720_120000",
  "steps": [
    {"step": "ingest", "status": "success", "response": {...}},
    {"step": "train", "status": "success", "response": {...}},
    {"step": "reload_model", "status": "success", "response": {...}}
  ]
}
```

### `POST /pipeline/run/{step_name}`
Trigger a single pipeline step by name (`ingest`, `train`, or `reload_model`).

### `POST /scheduler/start`
Start the automatic scheduler.

### `POST /scheduler/stop`
Stop the automatic scheduler.

### `GET /scheduler/status`
Check if the scheduler is running.

### `GET /cluster/health`
Aggregate health status from all nodes (calls each node's `/health` endpoint).

**Response:**
```json
{
  "nodes": {
    "pawn": {"status": "reachable", "response": {...}},
    "knight": {"status": "reachable", "response": {...}},
    "rook": {"status": "reachable", "response": {...}}
  }
}
```

## Configuration

### `config/pipeline_config.yaml`

| Key | Type | Default | Description |
|---|---|---|---|
| `ssh_user` | string | `artur` | SSH user for all nodes |
| `nodes` | dict | (see file) | Node hostnames and API ports |
| `schedule_interval_hours` | int | `6` | Hours between automatic pipeline runs |
| `pipeline_steps` | list | (see file) | Ordered list of pipeline steps |
| `log_dir` | string | `/logs` | Where to write pipeline logs |

### Pipeline Steps

Each step in `pipeline_steps` has:

| Field | Description |
|---|---|
| `name` | Step identifier |
| `node` | Which node to call (key in `nodes`) |
| `method` | HTTP method (`POST` or `GET`) |
| `path` | API endpoint path |
| `body` | JSON request body |
| `timeout` | Request timeout in seconds |

## Docker Details

Two containers run on queen-cluster:

### MLflow Server
- **Image:** `ghcr.io/mlflow/mlflow:latest`
- **Port:** `5000`
- **Volume:** `/home/artur/ORCHESTRATION/mlflow` → `/mlflow`
- **Backend:** SQLite at `/mlflow/mlflow.db`

### Orchestrator
- **Base image:** `python:3.12-slim`
- **Port:** `8083`
- **Volume:** `/home/artur/ORCHESTRATION/logs` → `/logs`
- **Depends on:** MLflow container
- **Restart policy:** `unless-stopped`
