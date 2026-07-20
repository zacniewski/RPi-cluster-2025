# Deployment Guide

Step-by-step tutorial to deploy the complete MLOps system on your four-node Raspberry Pi 5 cluster.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Step 1 — Clone the Repository](#step-1--clone-the-repository)
- [Step 2 — Configure the Cluster](#step-2--configure-the-cluster)
- [Step 3 — Deploy queen-cluster (Orchestration + MLflow)](#step-3--deploy-queen-cluster-orchestration--mlflow)
- [Step 4 — Deploy pawn-cluster (Data Ingestion)](#step-4--deploy-pawn-cluster-data-ingestion)
- [Step 5 — Deploy knight-cluster (Training)](#step-5--deploy-knight-cluster-training)
- [Step 6 — Deploy rook-cluster (Model Serving)](#step-6--deploy-rook-cluster-model-serving)
- [Step 7 — Run the First Pipeline](#step-7--run-the-first-pipeline)
- [Step 8 — Verify Everything Works](#step-8--verify-everything-works)
- [Automated Deployment (Alternative)](#automated-deployment-alternative)

---

## Prerequisites

Before starting, make sure the following are in place on **all four nodes**:

| Requirement | How to check | Setup guide |
|---|---|---|
| Raspberry Pi OS (64-bit) on NVMe | `uname -m` → `aarch64` | [04_installing_OS_on_RPi-NVMe_disk.md](../../docs/04_installing_OS_on_RPi-NVMe_disk.md) |
| Docker + Docker Compose | `docker --version` | [05_installing_Docker_on_RPi.md](../../docs/05_installing_Docker_on_RPi.md) |
| `uv` Python tooling | `uv --version` | [06_uv_and_Django_on_RPi.md](../../docs/06_uv_and_Django_on_RPi.md) |
| Passwordless SSH between nodes | `ssh knight-cluster echo ok` | [07_git_and_passwordless_SSH_configuration.md](../../docs/07_git_and_passwordless_SSH_configuration.md) |
| Nodes on the same local network | `ping pawn-cluster` | Physical Gigabit switch |

Make sure hostnames resolve. If not using DNS, add entries to `/etc/hosts` on each node:

```bash
# Example — adjust IPs to match your network
192.168.0.101  pawn-cluster
192.168.0.102  knight-cluster
192.168.0.103  rook-cluster
192.168.0.104  queen-cluster
```

---

## Step 1 — Clone the Repository

On your **admin laptop** (or on `queen-cluster`):

```bash
git clone <your-repo-url> RPi-cluster-2025
cd RPi-cluster-2025/mlops_system
```

---

## Step 2 — Configure the Cluster

```bash
cp shared/config.env.example shared/config.env
nano shared/config.env
```

Edit the following values to match your setup:

```bash
CLUSTER_USER=artur              # SSH user on all nodes
PAWN_HOST=pawn-cluster          # hostname or IP
KNIGHT_HOST=knight-cluster
ROOK_HOST=rook-cluster
QUEEN_HOST=queen-cluster
```

All other defaults are sensible for the demo. Save and close.

---

## Step 3 — Deploy queen-cluster (Orchestration + MLflow)

Deploy queen first because the other nodes depend on the MLflow tracking server.

**Option A — From your laptop (remote deploy):**

```bash
# Copy files to queen-cluster
rsync -az queen_orchestration/ artur@queen-cluster:/home/artur/ORCHESTRATION/app/

# SSH in and deploy
ssh artur@queen-cluster
cd /home/artur/ORCHESTRATION/app
mkdir -p /home/artur/ORCHESTRATION/{mlflow/artifacts,logs}
docker compose up -d --build
```

**Option B — Directly on queen-cluster:**

```bash
cd /path/to/mlops_system/queen_orchestration
bash deploy.sh
```

**Verify:**

```bash
# MLflow UI should be accessible
curl http://queen-cluster:5000/
# Dashboard API
curl http://queen-cluster:8083/health
```

Expected response from `/health`:
```json
{"service": "queen-orchestration", "status": "healthy", "scheduler_running": true}
```

---

## Step 4 — Deploy pawn-cluster (Data Ingestion)

**From your laptop:**

```bash
rsync -az pawn_data_ingestion/ artur@pawn-cluster:/home/artur/DATA/app/

ssh artur@pawn-cluster
cd /home/artur/DATA/app
mkdir -p /home/artur/DATA/{raw,processed,logs}
docker compose up -d --build
```

**Verify:**

```bash
curl http://pawn-cluster:8081/health
```

**Run an initial ingestion to generate demo data:**

```bash
# On pawn-cluster
docker compose exec pawn-ingestion python src/ingest.py --push
```

This loads the Iris dataset, validates it, saves it, and pushes it to knight-cluster.

---

## Step 5 — Deploy knight-cluster (Training)

```bash
rsync -az knight_training/ artur@knight-cluster:/home/artur/TRAINING/app/

ssh artur@knight-cluster
cd /home/artur/TRAINING/app
mkdir -p /home/artur/TRAINING/{data,models,logs}
docker compose up -d --build
```

**Verify:**

```bash
curl http://knight-cluster:8082/health
```

**Run an initial training job:**

```bash
# On knight-cluster
docker compose exec knight-training python src/train.py --push
```

This trains a Random Forest on the Iris data, logs metrics to MLflow, and pushes the model to rook-cluster.

Check MLflow at `http://queen-cluster:5000` — you should see the first experiment run.

---

## Step 6 — Deploy rook-cluster (Model Serving)

```bash
rsync -az rook_serving/ artur@rook-cluster:/home/artur/SERVING/app/

ssh artur@rook-cluster
cd /home/artur/SERVING/app
mkdir -p /home/artur/SERVING/{models,logs}
docker compose up -d --build
```

**Verify:**

```bash
curl http://rook-cluster:8080/health
```

Expected response:
```json
{"service": "rook-model-serving", "status": "healthy", "model_loaded": true, "model_version": "latest.joblib"}
```

**Test a prediction:**

```bash
curl -X POST http://rook-cluster:8080/predict \
  -H "Content-Type: application/json" \
  -d '{"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2}'
```

Expected response:
```json
{"prediction": 0, "label": "setosa", "confidence": 1.0, "model_version": "latest.joblib"}
```

---

## Step 7 — Run the First Pipeline

Trigger a full end-to-end pipeline from queen-cluster:

```bash
curl -X POST http://queen-cluster:8083/pipeline/run
```

Or via the API docs at `http://queen-cluster:8083/docs`.

The pipeline will:
1. Call pawn-cluster to ingest and push data
2. Call knight-cluster to train and push the model
3. Call rook-cluster to reload the new model

---

## Step 8 — Verify Everything Works

Run the health check script from your laptop:

```bash
cd mlops_system
bash shared/healthcheck.sh
```

You should see all services marked with ✓.

**Check the cluster health endpoint:**

```bash
curl http://queen-cluster:8083/cluster/health
```

**Browse the interactive API docs:**

| Node | URL |
|---|---|
| pawn-cluster | `http://pawn-cluster:8081/docs` |
| knight-cluster | `http://knight-cluster:8082/docs` |
| rook-cluster | `http://rook-cluster:8080/docs` |
| queen-cluster | `http://queen-cluster:8083/docs` |
| MLflow | `http://queen-cluster:5000` |

---

## Automated Deployment (Alternative)

If you prefer a one-command deployment from your laptop:

```bash
cd mlops_system
cp shared/config.env.example shared/config.env
nano shared/config.env    # edit with your values
bash shared/deploy_all.sh
```

This script will:
1. rsync each node's code to the target host
2. Build and start Docker containers on each node
3. Print a summary of all service URLs

> **Note:** The automated script requires passwordless SSH from your laptop to all four nodes.
