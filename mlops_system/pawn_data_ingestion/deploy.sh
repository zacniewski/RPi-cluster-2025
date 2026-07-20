#!/usr/bin/env bash
# Deploy pawn-cluster data ingestion service (run ON pawn-cluster)
set -euo pipefail

echo "[pawn-cluster] Creating data directories..."
mkdir -p /home/artur/DATA/{raw,processed,logs}

echo "[pawn-cluster] Building and starting container..."
docker compose down --remove-orphans 2>/dev/null || true
docker compose up -d --build

echo "[pawn-cluster] Running initial ingestion (demo data)..."
docker compose exec pawn-ingestion python src/ingest.py

echo "[pawn-cluster] ✓ Deployment complete."
echo "  API: http://$(hostname):8081/health"
echo "  Docs: http://$(hostname):8081/docs"
