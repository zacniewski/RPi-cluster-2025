# Rook-Cluster — Model Serving Node

Detailed documentation for the model serving API running on `rook-cluster`.

## Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Directory Layout](#directory-layout)
- [API Reference](#api-reference)
- [Model Hot-Reload](#model-hot-reload)
- [Prediction Logging](#prediction-logging)
- [Docker Details](#docker-details)
- [Switching to a New Task](#switching-to-a-new-task)

---

## Overview

The rook node **serves the trained model** as a REST API. Any client on the local network can send feature values and receive a prediction. It:

1. **Loads** the latest model artifact pushed by knight-cluster
2. **Serves** predictions via `POST /predict` and `POST /predict/batch`
3. **Hot-reloads** — a background watcher detects new model files and swaps them in without downtime
4. **Logs** every prediction request and response for later analysis

## Architecture

```
                                    ┌──────────────────────┐
  model from knight ──────────────► │    rook-cluster       │
                                    │                       │
  client request ──────────────────►│  api.py (FastAPI)     │
                                    │    ├─ /predict        │
                                    │    ├─ /predict/batch  │
                                    │    ├─ /health         │
                                    │    └─ /reload         │
                                    │                       │
                                    │  model_loader.py      │
                                    │    └─ watcher thread  │
                                    │                       │
  prediction response ◄─────────────│  logs/                │
                                    │  prediction_log.jsonl │
                                    └──────────────────────┘
```

## Directory Layout

```
/home/artur/SERVING/
├── models/                 # Model artifacts from knight-cluster
│   ├── model_20250720_120500.joblib
│   └── latest.joblib → model_20250720_120500.joblib
├── logs/                   # Prediction logs
│   └── prediction_log.jsonl
└── app/                    # Application code
    ├── Dockerfile
    ├── docker-compose.yml
    └── src/
```

## API Reference

Base URL: `http://rook-cluster:8080`

Interactive docs: `http://rook-cluster:8080/docs`

### `GET /health`

Returns service status and currently loaded model.

**Response:**
```json
{
  "service": "rook-model-serving",
  "status": "healthy",
  "model_loaded": true,
  "model_version": "latest.joblib"
}
```

If no model is loaded, `status` will be `"no_model"` and `model_loaded` will be `false`.

### `POST /predict`

Single prediction.

**Request:**
```json
{
  "sepal_length": 5.1,
  "sepal_width": 3.5,
  "petal_length": 1.4,
  "petal_width": 0.2
}
```

**Response:**
```json
{
  "prediction": 0,
  "label": "setosa",
  "confidence": 1.0,
  "model_version": "latest.joblib"
}
```

### `POST /predict/batch`

Multiple predictions in one call.

**Request:**
```json
{
  "instances": [
    {"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2},
    {"sepal_length": 6.7, "sepal_width": 3.0, "petal_length": 5.2, "petal_width": 2.3}
  ]
}
```

**Response:**
```json
{
  "predictions": [
    {"prediction": 0, "label": "setosa", "confidence": 1.0, "model_version": "latest.joblib"},
    {"prediction": 2, "label": "virginica", "confidence": 0.98, "model_version": "latest.joblib"}
  ]
}
```

### `POST /reload`

Force the model to reload from disk (useful after manually copying a new model file).

**Response:**
```json
{"status": "reloaded", "model_version": "latest.joblib"}
```

## Model Hot-Reload

The `ModelManager` class in `src/model_loader.py` runs a background watcher thread that:

1. Checks the `/models` directory every **10 seconds**
2. Looks for `latest.joblib` (or `latest.pkl`) symlink
3. Compares the resolved file's modification time with the last loaded version
4. If a newer file is found, loads it and atomically swaps the model reference

This means you can push a new model from knight-cluster and it will be picked up automatically within 10 seconds — no restart needed.

## Prediction Logging

Every prediction is appended to `/logs/prediction_log.jsonl` in this format:

```json
{
  "timestamp": "2025-07-20T12:05:30.123456+00:00",
  "request": {"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2},
  "response": {"prediction": 0, "label": "setosa", "confidence": 1.0, "model_version": "latest.joblib"}
}
```

These logs can be synced to queen-cluster for monitoring and drift detection.

## Docker Details

- **Base image:** `python:3.12-slim`
- **Exposed port:** `8080`
- **Volumes:**
  - `/home/artur/SERVING/models` → `/models`
  - `/home/artur/SERVING/logs` → `/logs`
- **Restart policy:** `unless-stopped`

## Switching to a New Task

To serve a different model (e.g., a regression model on a different dataset):

1. **Update `src/schemas.py`** — change `PredictRequest` fields to match your new features
2. **Update `src/model_loader.py`** — change `CLASS_LABELS` to match your new target classes (or remove for regression)
3. **Update `src/api.py`** — adjust the feature extraction in the `/predict` endpoint
4. Rebuild: `docker compose up -d --build`

The model file format (joblib/pickle) and hot-reload mechanism stay the same regardless of the task.
