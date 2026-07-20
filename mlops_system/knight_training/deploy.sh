#!/usr/bin/env bash
# Deploy knight-cluster training service (run ON knight-cluster)
set -euo pipefail

echo "[knight-cluster] Creating directories..."
mkdir -p /home/artur/TRAINING/{data,models,logs}

echo "[knight-cluster] Building and starting container..."
docker compose down --remove-orphans 2>/dev/null || true
docker compose up -d --build

echo "[knight-cluster] ✓ Deployment complete."
echo "  API: http://$(hostname):8082/health"
echo "  Docs: http://$(hostname):8082/docs"
