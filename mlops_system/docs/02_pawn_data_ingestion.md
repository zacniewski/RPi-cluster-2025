# Pawn-Cluster — Data Ingestion Node

Detailed documentation for the data ingestion service running on `pawn-cluster`.

## Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Directory Layout](#directory-layout)
- [Configuration](#configuration)
- [Data Sources](#data-sources)
- [Validation Engine](#validation-engine)
- [API Reference](#api-reference)
- [CLI Usage](#cli-usage)
- [Docker Details](#docker-details)
- [Adding a New Dataset](#adding-a-new-dataset)

---

## Overview

The pawn node is the **entry point for all data** in the MLOps pipeline. It:

1. **Ingests** raw data from a configurable source (built-in demo, CSV file, or remote API)
2. **Validates** the data against a set of rules (schema, types, ranges, missing values)
3. **Stores** both raw and processed versions with timestamps
4. **Pushes** the cleaned dataset to `knight-cluster` via rsync over SSH

## Architecture

```
┌──────────────────────────────────────────────────┐
│                  pawn-cluster                      │
│                                                    │
│  ┌──────────┐    ┌───────────┐    ┌────────────┐  │
│  │ ingest.py│───►│validate.py│───►│ processed/  │──┼──► knight-cluster
│  │          │    │           │    │ latest.csv  │  │    (rsync/SSH)
│  └──────────┘    └───────────┘    └────────────┘  │
│       │                                │           │
│       ▼                                ▼           │
│  ┌──────────┐                    ┌────────────┐   │
│  │  raw/    │                    │   logs/     │   │
│  └──────────┘                    └────────────┘   │
│                                                    │
│  ┌──────────────────────────────────────────────┐ │
│  │  api.py (FastAPI on port 8081)                │ │
│  │  GET /health  ·  POST /ingest  ·  GET /data  │ │
│  └──────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────┘
```

## Directory Layout

On the node:
```
/home/artur/DATA/
├── raw/                    # Untouched incoming files (timestamped)
│   ├── raw_20250720_120000.csv
│   └── ...
├── processed/              # Cleaned and validated datasets
│   ├── dataset_20250720_120000.csv
│   ├── latest.csv → dataset_20250720_120000.csv
│   └── ...
├── logs/                   # Ingestion run logs
│   └── ingestion_log.jsonl
└── app/                    # Application code (deployed here)
    ├── Dockerfile
    ├── docker-compose.yml
    ├── src/
    └── config/
```

## Configuration

### `config/ingestion_config.yaml`

| Key | Type | Default | Description |
|---|---|---|---|
| `source_type` | string | `demo_iris` | Data source: `demo_iris`, `csv_file`, or `api` |
| `csv_path` | string | `/data/raw/input.csv` | Path to CSV file (when `source_type: csv_file`) |
| `api_url` | string | `""` | Remote API URL (when `source_type: api`) |
| `api_headers` | dict | `{}` | HTTP headers for API requests |
| `raw_dir` | string | `/data/raw` | Where to save raw data |
| `processed_dir` | string | `/data/processed` | Where to save validated data |
| `log_dir` | string | `/data/logs` | Where to write logs |
| `knight_host` | string | `knight-cluster` | Training node hostname |
| `knight_user` | string | `artur` | SSH user on knight-cluster |
| `knight_data_dir` | string | `/home/artur/TRAINING/data` | Destination path on knight |
| `timestamp_format` | string | `%Y%m%d_%H%M%S` | Timestamp format for file names |

### `config/validation_rules.yaml`

| Key | Type | Description |
|---|---|---|
| `required_columns` | list | Columns that must exist |
| `column_types` | dict | Expected dtype per column |
| `range_checks` | dict | Min/max bounds per numeric column |
| `max_missing_pct` | float | Maximum % of missing values allowed per column |
| `min_rows` | int | Minimum number of rows required |

## Data Sources

### `demo_iris` (default)
Loads the Iris dataset from scikit-learn. No external files needed. Perfect for testing the pipeline end-to-end.

### `csv_file`
Reads a CSV from `csv_path`. Place your file in `/home/artur/DATA/raw/input.csv` (or change the path in config).

### `api`
Fetches JSON from `api_url` and converts it to a DataFrame. Set `api_headers` for authentication if needed.

## Validation Engine

The validation engine (`src/validate.py`) runs five checks in order:

1. **Required columns** — all columns listed in `required_columns` must exist
2. **Column types** — each column's dtype must match `column_types` (auto-casting is attempted)
3. **Range checks** — numeric values must fall within `range_checks` bounds
4. **Missing values** — no column may exceed `max_missing_pct` percent missing
5. **Minimum rows** — the dataset must have at least `min_rows` rows

If any check fails, the ingestion is marked as `FAILED` and the data is **not** pushed to knight-cluster.

## API Reference

Base URL: `http://pawn-cluster:8081`

### `GET /health`
Returns service status and last ingestion result.

### `POST /ingest`
Triggers an ingestion run.

**Request body:**
```json
{
  "source": "demo_iris",
  "push": true
}
```

**Response:**
```json
{
  "status": "success",
  "timestamp": "20250720_120000",
  "rows": 150,
  "columns": 5
}
```

### `GET /data/status`
Returns information about the latest processed dataset.

### `GET /docs`
Interactive Swagger UI documentation.

## CLI Usage

Run the ingestion script directly inside the container:

```bash
# Default ingestion (demo data, no push)
docker compose exec pawn-ingestion python src/ingest.py

# Ingest and push to knight-cluster
docker compose exec pawn-ingestion python src/ingest.py --push

# Override source type
docker compose exec pawn-ingestion python src/ingest.py --source csv_file --push
```

## Docker Details

- **Base image:** `python:3.12-slim`
- **Exposed port:** `8081`
- **Volumes:**
  - `/home/artur/DATA/raw` → `/data/raw`
  - `/home/artur/DATA/processed` → `/data/processed`
  - `/home/artur/DATA/logs` → `/data/logs`
  - `~/.ssh` → `/root/.ssh` (read-only, for rsync)
- **Restart policy:** `unless-stopped`

## Adding a New Dataset

1. Edit `config/validation_rules.yaml` — update `required_columns`, `column_types`, and `range_checks`
2. Edit `config/ingestion_config.yaml` — set `source_type` and the relevant path/URL
3. Rebuild: `docker compose up -d --build`
4. Test: `docker compose exec pawn-ingestion python src/ingest.py`
