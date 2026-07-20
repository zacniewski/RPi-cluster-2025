# Usage Guide

Day-to-day operations for the MLOps system on the Raspberry Pi cluster.

## Table of Contents
- [Quick Reference](#quick-reference)
- [Running a Full Pipeline](#running-a-full-pipeline)
- [Running Individual Steps](#running-individual-steps)
- [Making Predictions](#making-predictions)
- [Viewing Experiment Results](#viewing-experiment-results)
- [Monitoring Cluster Health](#monitoring-cluster-health)
- [Managing the Scheduler](#managing-the-scheduler)
- [Updating the System](#updating-the-system)
- [Using Your Own Data](#using-your-own-data)
- [Changing the Model](#changing-the-model)
- [Viewing Logs](#viewing-logs)
- [Backing Up Data](#backing-up-data)

---

## Quick Reference

| Action | Command |
|---|---|
| Run full pipeline | `curl -X POST http://queen-cluster:8083/pipeline/run` |
| Make a prediction | `curl -X POST http://rook-cluster:8080/predict -H "Content-Type: application/json" -d '{"sepal_length":5.1,"sepal_width":3.5,"petal_length":1.4,"petal_width":0.2}'` |
| Check cluster health | `bash shared/healthcheck.sh` |
| View MLflow UI | Open `http://queen-cluster:5000` in browser |
| View API docs | Open `http://<node>:<port>/docs` in browser |
| Start scheduler | `curl -X POST http://queen-cluster:8083/scheduler/start` |
| Stop scheduler | `curl -X POST http://queen-cluster:8083/scheduler/stop` |

---

## Running a Full Pipeline

### Via the API (recommended)

```bash
curl -X POST http://queen-cluster:8083/pipeline/run
```

This triggers: ingest → train → reload model. The response shows the result of each step.

### Via the CLI

```bash
ssh artur@queen-cluster
cd /home/artur/ORCHESTRATION/app
docker compose exec orchestrator python src/pipeline_runner.py
```

### Via the Swagger UI

Open `http://queen-cluster:8083/docs`, find `POST /pipeline/run`, and click "Try it out".

---

## Running Individual Steps

### Ingest only

```bash
curl -X POST http://queen-cluster:8083/pipeline/run/ingest
```

Or directly on pawn-cluster:
```bash
curl -X POST http://pawn-cluster:8081/ingest \
  -H "Content-Type: application/json" \
  -d '{"source": "demo_iris", "push": true}'
```

### Train only

```bash
curl -X POST http://queen-cluster:8083/pipeline/run/train
```

Or directly on knight-cluster:
```bash
curl -X POST http://knight-cluster:8082/train \
  -H "Content-Type: application/json" \
  -d '{"model_type": "random_forest", "push": true}'
```

### Reload model only

```bash
curl -X POST http://queen-cluster:8083/pipeline/run/reload_model
```

Or directly on rook-cluster:
```bash
curl -X POST http://rook-cluster:8080/reload
```

---

## Making Predictions

### Single prediction

```bash
curl -X POST http://rook-cluster:8080/predict \
  -H "Content-Type: application/json" \
  -d '{
    "sepal_length": 5.1,
    "sepal_width": 3.5,
    "petal_length": 1.4,
    "petal_width": 0.2
  }'
```

### Batch prediction

```bash
curl -X POST http://rook-cluster:8080/predict/batch \
  -H "Content-Type: application/json" \
  -d '{
    "instances": [
      {"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2},
      {"sepal_length": 6.7, "sepal_width": 3.0, "petal_length": 5.2, "petal_width": 2.3},
      {"sepal_length": 5.8, "sepal_width": 2.7, "petal_length": 4.1, "petal_width": 1.0}
    ]
  }'
```

### Python client example

```python
import httpx

response = httpx.post(
    "http://rook-cluster:8080/predict",
    json={"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2},
)
print(response.json())
# {"prediction": 0, "label": "setosa", "confidence": 1.0, "model_version": "latest.joblib"}
```

---

## Viewing Experiment Results

Open `http://queen-cluster:5000` in your browser.

- Click an experiment name to see all runs
- Click a run to see parameters, metrics, and artifacts
- Use the "Compare" button to compare multiple runs side by side
- Download model artifacts from the "Artifacts" tab

---

## Monitoring Cluster Health

### Health check script

```bash
cd mlops_system
bash shared/healthcheck.sh
```

### Cluster health API

```bash
curl http://queen-cluster:8083/cluster/health
```

### Individual node health

```bash
curl http://pawn-cluster:8081/health
curl http://knight-cluster:8082/health
curl http://rook-cluster:8080/health
curl http://queen-cluster:8083/health
```

### Docker container status

```bash
# On any node
ssh artur@<node> docker ps
```

---

## Managing the Scheduler

The scheduler runs the full pipeline automatically on a configurable interval (default: every 6 hours).

```bash
# Check status
curl http://queen-cluster:8083/scheduler/status

# Stop automatic runs
curl -X POST http://queen-cluster:8083/scheduler/stop

# Restart automatic runs
curl -X POST http://queen-cluster:8083/scheduler/start
```

To change the interval, edit `queen_orchestration/config/pipeline_config.yaml`:

```yaml
schedule_interval_hours: 12  # run every 12 hours instead
```

Then rebuild: `docker compose up -d --build` on queen-cluster.

---

## Updating the System

After making code changes on your laptop:

```bash
# Re-deploy a single node (example: knight)
rsync -az knight_training/ artur@knight-cluster:/home/artur/TRAINING/app/
ssh artur@knight-cluster "cd /home/artur/TRAINING/app && docker compose up -d --build"

# Or re-deploy everything
bash shared/deploy_all.sh
```

---

## Using Your Own Data

1. **Prepare your CSV** with feature columns and a target column
2. **Copy it to pawn-cluster:**
   ```bash
   scp my_data.csv artur@pawn-cluster:/home/artur/DATA/raw/input.csv
   ```
3. **Update pawn config** (`pawn_data_ingestion/config/ingestion_config.yaml`):
   ```yaml
   source_type: csv_file
   csv_path: /data/raw/input.csv
   ```
4. **Update validation rules** (`pawn_data_ingestion/config/validation_rules.yaml`) to match your schema
5. **Update knight config** (`knight_training/config/training_config.yaml`) — set `target_column` and optionally `feature_columns`
6. **Update rook schemas** (`rook_serving/src/schemas.py`) — change `PredictRequest` fields
7. **Redeploy** the affected nodes

---

## Changing the Model

Edit `knight_training/config/training_config.yaml`:

```yaml
model_type: gradient_boosting  # or logistic_regression
```

Then either:
- Trigger a new training run: `curl -X POST http://knight-cluster:8082/train -H "Content-Type: application/json" -d '{"push": true}'`
- Or redeploy and run the pipeline

---

## Viewing Logs

All logs are stored as JSONL (one JSON object per line):

```bash
# Ingestion logs
ssh artur@pawn-cluster "cat /home/artur/DATA/logs/ingestion_log.jsonl"

# Training logs
ssh artur@knight-cluster "cat /home/artur/TRAINING/logs/training_log.jsonl"

# Prediction logs
ssh artur@rook-cluster "cat /home/artur/SERVING/logs/prediction_log.jsonl"

# Pipeline logs
ssh artur@queen-cluster "cat /home/artur/ORCHESTRATION/logs/pipeline_log.jsonl"
```

Use `jq` for pretty-printing:
```bash
ssh artur@queen-cluster "cat /home/artur/ORCHESTRATION/logs/pipeline_log.jsonl" | jq .
```

---

## Backing Up Data

Key directories to back up:

| Node | Path | Contains |
|---|---|---|
| queen-cluster | `/home/artur/ORCHESTRATION/mlflow/` | MLflow database and artifacts |
| pawn-cluster | `/home/artur/DATA/processed/` | Processed datasets |
| knight-cluster | `/home/artur/TRAINING/models/` | Trained model artifacts |
| rook-cluster | `/home/artur/SERVING/logs/` | Prediction logs |

Example backup to your laptop:
```bash
rsync -az artur@queen-cluster:/home/artur/ORCHESTRATION/mlflow/ ./backup/mlflow/
rsync -az artur@knight-cluster:/home/artur/TRAINING/models/ ./backup/models/
```
