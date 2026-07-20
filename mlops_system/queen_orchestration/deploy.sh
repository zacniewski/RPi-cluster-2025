#!/usr/bin/env bash
# Deploy queen-cluster orchestration + MLflow (run ON queen-cluster)
set -euo pipefail

echo "[queen-cluster] Creating directories..."
mkdir -p /home/artur/ORCHESTRATION/{mlflow/artifacts,logs}

echo "[queen-cluster] Building and starting containers..."
docker compose down --remove-orphans 2>/dev/null || true
docker compose up -d --build

echo "[queen-cluster] ✓ Deployment complete."
echo "  MLflow UI:    http://$(hostname):5000"
echo "  Dashboard:    http://$(hostname):8083/health"
echo "  API Docs:     http://$(hostname):8083/docs"
