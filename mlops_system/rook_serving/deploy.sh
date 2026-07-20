#!/usr/bin/env bash
# Deploy rook-cluster model serving service (run ON rook-cluster)
set -euo pipefail

echo "[rook-cluster] Creating directories..."
mkdir -p /home/artur/SERVING/{models,logs}

echo "[rook-cluster] Building and starting container..."
docker compose down --remove-orphans 2>/dev/null || true
docker compose up -d --build

echo "[rook-cluster] ✓ Deployment complete."
echo "  API: http://$(hostname):8080/health"
echo "  Docs: http://$(hostname):8080/docs"
echo "  Note: The API will return 503 until a model is deployed."
