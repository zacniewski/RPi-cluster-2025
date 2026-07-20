# MLOps System for Raspberry Pi Cluster

A complete, ready-to-deploy MLOps system designed for a four-node Raspberry Pi 5 cluster.
Each node has a dedicated role that mirrors a real production MLOps stage.

## Cluster Nodes

| Node | IP (example) | Role | Directory |
|---|---|---|---|
| `pawn-cluster` | `192.168.0.101` | Data Ingestion | `pawn_data_ingestion/` |
| `knight-cluster` | `192.168.0.102` | Model Training | `knight_training/` |
| `rook-cluster` | `192.168.0.103` | Model Serving | `rook_serving/` |
| `queen-cluster` | `192.168.0.104` | Orchestration & Tracking | `queen_orchestration/` |

## Quick Start

See [docs/01_deployment_guide.md](docs/01_deployment_guide.md) for the full step-by-step deployment tutorial.

**TL;DR** — deploy the entire system from your laptop:

```bash
# 1. Edit shared config with your actual IPs and user
cp shared/config.env.example shared/config.env
nano shared/config.env

# 2. Run the deployment script
bash shared/deploy_all.sh
```

## Architecture

```
┌─────────────-┐    cleaned data    ┌──────────────┐   model artifact   ┌──────────────┐
│    pawn      │ ────────────────►  │   knight     │ ────────────────►  │    rook      │
│  (ingest)    │                    │  (train)     │                    │   (serve)    │
└──────┬───────┘                    └──────┬───────┘                    └──────┬───────┘
       │ status                            │ metrics                          │ health
       ▼                                   ▼                                  ▼
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                          queen (orchestrate + track)                                 │
│                     MLflow · Scheduler · Dashboard                                   │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

## Documentation

| Document | Description |
|---|---|
| [docs/01_deployment_guide.md](docs/01_deployment_guide.md) | Step-by-step deployment tutorial |
| [docs/02_pawn_data_ingestion.md](docs/02_pawn_data_ingestion.md) | Data ingestion node details |
| [docs/03_knight_training.md](docs/03_knight_training.md) | Training node details |
| [docs/04_rook_serving.md](docs/04_rook_serving.md) | Model serving node details |
| [docs/05_queen_orchestration.md](docs/05_queen_orchestration.md) | Orchestration node details |
| [docs/06_usage_guide.md](docs/06_usage_guide.md) | Day-to-day usage and operations |
| [docs/07_troubleshooting.md](docs/07_troubleshooting.md) | Common issues and solutions |

## Prerequisites

- Four Raspberry Pi 5 nodes with Raspberry Pi OS (64-bit)
- Docker installed on all nodes ([05_installing_Docker_on_RPi.md](../docs/05_installing_Docker_on_RPi.md))
- `uv` installed on all nodes ([06_uv_and_Django_on_RPi.md](../docs/06_uv_and_Django_on_RPi.md))
- Passwordless SSH between all nodes ([07_git_and_passwordless_SSH_configuration.md](../docs/07_git_and_passwordless_SSH_configuration.md))
- All nodes connected via a Gigabit switch on the same local network

## Project Structure

```
mlops_system/
├── README.md                    # This file
├── shared/                      # Shared configs and deployment scripts
│   ├── config.env.example       # Template — copy to config.env and edit
│   ├── deploy_all.sh            # One-command full cluster deployment
│   └── healthcheck.sh           # Check status of all nodes
├── pawn_data_ingestion/         # Data ingestion node (pawn-cluster)
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── pyproject.toml
│   ├── src/
│   │   ├── ingest.py            # Main ingestion script
│   │   ├── validate.py          # Data validation logic
│   │   └── api.py               # Status API (FastAPI)
│   ├── config/
│   │   ├── ingestion_config.yaml
│   │   └── validation_rules.yaml
│   └── deploy.sh
├── knight_training/             # Training node (knight-cluster)
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── pyproject.toml
│   ├── src/
│   │   ├── train.py             # Training script
│   │   ├── evaluate.py          # Model evaluation
│   │   └── export_model.py      # Model export and push
│   ├── config/
│   │   └── training_config.yaml
│   └── deploy.sh
├── rook_serving/                # Model serving node (rook-cluster)
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── pyproject.toml
│   ├── src/
│   │   ├── api.py               # FastAPI prediction API
│   │   ├── model_loader.py      # Model loading and hot-reload
│   │   └── schemas.py           # Pydantic request/response schemas
│   └── deploy.sh
├── queen_orchestration/         # Orchestration node (queen-cluster)
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── pyproject.toml
│   ├── src/
│   │   ├── pipeline_runner.py   # End-to-end pipeline orchestrator
│   │   ├── scheduler.py         # APScheduler-based scheduler
│   │   └── dashboard_api.py     # Pipeline status API
│   ├── config/
│   │   └── pipeline_config.yaml
│   └── deploy.sh
└── docs/                        # Detailed documentation
    ├── 01_deployment_guide.md
    ├── 02_pawn_data_ingestion.md
    ├── 03_knight_training.md
    ├── 04_rook_serving.md
    ├── 05_queen_orchestration.md
    ├── 06_usage_guide.md
    └── 07_troubleshooting.md
```
