# Knight-Cluster — Training Node

Detailed documentation for the model training service running on `knight-cluster`.

## Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Directory Layout](#directory-layout)
- [Configuration](#configuration)
- [Supported Models](#supported-models)
- [MLflow Integration](#mlflow-integration)
- [API Reference](#api-reference)
- [CLI Usage](#cli-usage)
- [Docker Details](#docker-details)
- [Adding a New Model](#adding-a-new-model)

---

## Overview

The knight node is the **training engine** of the MLOps pipeline. It:

1. **Loads** the processed dataset pushed by pawn-cluster
2. **Trains** a scikit-learn classifier with configurable hyperparameters
3. **Evaluates** the model on a held-out test set (accuracy, F1, precision, recall)
4. **Logs** all parameters and metrics to the MLflow server on queen-cluster
5. **Exports** the trained model artifact and pushes it to rook-cluster

## Architecture

```
                                    ┌─────────────────┐
  dataset from pawn ──────────────► │  knight-cluster  │
                                    │                  │
                                    │  train.py        │
                                    │    ├─ load data  │
                                    │    ├─ split      │
                                    │    ├─ train      │
                                    │    ├─ evaluate   │──► MLflow (queen)
                                    │    └─ export     │
                                    │                  │
                                    │  models/         │──► rook-cluster
                                    │  latest.joblib   │    (rsync/SSH)
                                    └─────────────────┘
```

## Directory Layout

```
/home/artur/TRAINING/
├── data/                   # Datasets received from pawn-cluster
│   ├── dataset_20250720_120000.csv
│   └── latest.csv → dataset_20250720_120000.csv
├── models/                 # Trained model artifacts
│   ├── model_20250720_120500.joblib
│   └── latest.joblib → model_20250720_120500.joblib
├── logs/                   # Training run logs
│   └── training_log.jsonl
└── app/                    # Application code
    ├── Dockerfile
    ├── docker-compose.yml
    ├── src/
    └── config/
```

## Configuration

### `config/training_config.yaml`

| Key | Type | Default | Description |
|---|---|---|---|
| `dataset_path` | string | `/data/latest.csv` | Path to the training dataset |
| `target_column` | string | `target` | Name of the target column |
| `feature_columns` | list | `[]` (auto-detect) | Feature columns (empty = all except target) |
| `model_type` | string | `random_forest` | Model algorithm to use |
| `hyperparameters` | dict | (see below) | Per-model hyperparameters |
| `test_size` | float | `0.2` | Fraction of data for testing |
| `random_state` | int | `42` | Random seed for reproducibility |
| `model_dir` | string | `/models` | Where to save model artifacts |
| `log_dir` | string | `/logs` | Where to write logs |
| `mlflow_tracking_uri` | string | `http://queen-cluster:5000` | MLflow server URL |
| `mlflow_experiment_name` | string | `rpi-cluster-training` | MLflow experiment name |
| `export_format` | string | `joblib` | Model serialization format |
| `rook_host` | string | `rook-cluster` | Serving node hostname |
| `rook_user` | string | `artur` | SSH user on rook-cluster |
| `rook_model_dir` | string | `/home/artur/SERVING/models` | Destination path on rook |

### Default Hyperparameters

```yaml
hyperparameters:
  random_forest:
    n_estimators: 100
    max_depth: 10
    random_state: 42
  gradient_boosting:
    n_estimators: 100
    max_depth: 5
    learning_rate: 0.1
    random_state: 42
  logistic_regression:
    max_iter: 200
    random_state: 42
```

## Supported Models

| Model Type | scikit-learn Class | Best For |
|---|---|---|
| `random_forest` | `RandomForestClassifier` | General-purpose, robust baseline |
| `gradient_boosting` | `GradientBoostingClassifier` | Higher accuracy, slower training |
| `logistic_regression` | `LogisticRegression` | Fast, interpretable, linear problems |

To add more models, see [Adding a New Model](#adding-a-new-model).

## MLflow Integration

Every training run logs the following to MLflow on `queen-cluster:5000`:

- **Parameters:** model_type, all hyperparameters, dataset_rows
- **Metrics:** accuracy, f1_weighted, precision_weighted, recall_weighted
- **Artifacts:** the trained model file

Browse experiments at `http://queen-cluster:5000`.

If the MLflow server is unreachable, training continues without tracking (a warning is logged).

## API Reference

Base URL: `http://knight-cluster:8082`

### `GET /health`
Returns service status and last training result.

### `POST /train`
Triggers a training run.

**Request body:**
```json
{
  "model_type": "random_forest",
  "push": true
}
```

**Response:**
```json
{
  "status": "success",
  "timestamp": "20250720_120500",
  "model_path": "/models/model_20250720_120500.joblib",
  "accuracy": 0.9667,
  "f1_weighted": 0.9667,
  "precision_weighted": 0.9683,
  "recall_weighted": 0.9667
}
```

### `GET /docs`
Interactive Swagger UI documentation.

## CLI Usage

```bash
# Train with defaults
docker compose exec knight-training python src/train.py

# Train and push model to rook-cluster
docker compose exec knight-training python src/train.py --push

# Train with a specific model type
docker compose exec knight-training python src/train.py --model gradient_boosting --push
```

## Docker Details

- **Base image:** `python:3.12-slim`
- **Exposed port:** `8082`
- **Volumes:**
  - `/home/artur/TRAINING/data` → `/data`
  - `/home/artur/TRAINING/models` → `/models`
  - `/home/artur/TRAINING/logs` → `/logs`
  - `~/.ssh` → `/root/.ssh` (read-only, for rsync)
- **Environment:** `MLFLOW_TRACKING_URI=http://queen-cluster:5000`
- **Restart policy:** `unless-stopped`

## Adding a New Model

1. Edit `src/train.py` — add the new class to `MODEL_REGISTRY`:
   ```python
   from sklearn.svm import SVC
   MODEL_REGISTRY["svm"] = SVC
   ```
2. Edit `config/training_config.yaml` — add hyperparameters:
   ```yaml
   hyperparameters:
     svm:
       kernel: rbf
       C: 1.0
       random_state: 42
   ```
3. Rebuild: `docker compose up -d --build`
4. Train: `docker compose exec knight-training python src/train.py --model svm`
