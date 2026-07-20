#!/usr/bin/env bash
# =============================================================================
# deploy_all.sh — Deploy the entire MLOps system to all four RPi nodes
# =============================================================================
# Usage:
#   bash shared/deploy_all.sh
#
# Prerequisites:
#   - Passwordless SSH configured to all nodes
#   - Docker installed on all nodes
#   - shared/config.env exists (copy from config.env.example)
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG_FILE="$SCRIPT_DIR/config.env"

if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "ERROR: $CONFIG_FILE not found."
    echo "Run:  cp shared/config.env.example shared/config.env"
    echo "Then edit shared/config.env with your actual values."
    exit 1
fi

# shellcheck source=config.env.example
source "$CONFIG_FILE"

echo "============================================="
echo " MLOps Cluster Deployment"
echo "============================================="
echo " User:   $CLUSTER_USER"
echo " Pawn:   $PAWN_HOST"
echo " Knight: $KNIGHT_HOST"
echo " Rook:   $ROOK_HOST"
echo " Queen:  $QUEEN_HOST"
echo "============================================="
echo ""

# Helper: run a command on a remote node via SSH
remote() {
    local host="$1"
    shift
    ssh -o StrictHostKeyChecking=no "${CLUSTER_USER}@${host}" "$@"
}

# Helper: copy a directory to a remote node
sync_to() {
    local host="$1"
    local src="$2"
    local dest="$3"
    rsync -az --delete -e "ssh -o StrictHostKeyChecking=no" \
        "$src" "${CLUSTER_USER}@${host}:${dest}"
}

# -------------------------------------------------------
# Step 1: Deploy queen-cluster (MLflow + Orchestration)
# -------------------------------------------------------
echo "[1/4] Deploying queen-cluster ($QUEEN_HOST)..."
remote "$QUEEN_HOST" "mkdir -p $QUEEN_ORCHESTRATION_DIR"
sync_to "$QUEEN_HOST" "$PROJECT_DIR/queen_orchestration/" "$QUEEN_ORCHESTRATION_DIR/app/"
sync_to "$QUEEN_HOST" "$SCRIPT_DIR/config.env" "$QUEEN_ORCHESTRATION_DIR/config.env"
remote "$QUEEN_HOST" "cd $QUEEN_ORCHESTRATION_DIR/app && docker compose down --remove-orphans 2>/dev/null || true"
remote "$QUEEN_HOST" "cd $QUEEN_ORCHESTRATION_DIR/app && docker compose up -d --build"
echo "  ✓ queen-cluster deployed (MLflow at http://$QUEEN_HOST:$MLFLOW_PORT)"
echo ""

# -------------------------------------------------------
# Step 2: Deploy pawn-cluster (Data Ingestion)
# -------------------------------------------------------
echo "[2/4] Deploying pawn-cluster ($PAWN_HOST)..."
remote "$PAWN_HOST" "mkdir -p $PAWN_DATA_DIR/{raw,processed,logs}"
sync_to "$PAWN_HOST" "$PROJECT_DIR/pawn_data_ingestion/" "$PAWN_DATA_DIR/app/"
sync_to "$PAWN_HOST" "$SCRIPT_DIR/config.env" "$PAWN_DATA_DIR/config.env"
remote "$PAWN_HOST" "cd $PAWN_DATA_DIR/app && docker compose down --remove-orphans 2>/dev/null || true"
remote "$PAWN_HOST" "cd $PAWN_DATA_DIR/app && docker compose up -d --build"
echo "  ✓ pawn-cluster deployed (API at http://$PAWN_HOST:$PAWN_API_PORT)"
echo ""

# -------------------------------------------------------
# Step 3: Deploy knight-cluster (Training)
# -------------------------------------------------------
echo "[3/4] Deploying knight-cluster ($KNIGHT_HOST)..."
remote "$KNIGHT_HOST" "mkdir -p $KNIGHT_TRAINING_DIR/{data,models,logs}"
sync_to "$KNIGHT_HOST" "$PROJECT_DIR/knight_training/" "$KNIGHT_TRAINING_DIR/app/"
sync_to "$KNIGHT_HOST" "$SCRIPT_DIR/config.env" "$KNIGHT_TRAINING_DIR/config.env"
remote "$KNIGHT_HOST" "cd $KNIGHT_TRAINING_DIR/app && docker compose down --remove-orphans 2>/dev/null || true"
remote "$KNIGHT_HOST" "cd $KNIGHT_TRAINING_DIR/app && docker compose up -d --build"
echo "  ✓ knight-cluster deployed (API at http://$KNIGHT_HOST:$KNIGHT_API_PORT)"
echo ""

# -------------------------------------------------------
# Step 4: Deploy rook-cluster (Model Serving)
# -------------------------------------------------------
echo "[4/4] Deploying rook-cluster ($ROOK_HOST)..."
remote "$ROOK_HOST" "mkdir -p $ROOK_SERVING_DIR/{models,logs}"
sync_to "$ROOK_HOST" "$PROJECT_DIR/rook_serving/" "$ROOK_SERVING_DIR/app/"
sync_to "$ROOK_HOST" "$SCRIPT_DIR/config.env" "$ROOK_SERVING_DIR/config.env"
remote "$ROOK_HOST" "cd $ROOK_SERVING_DIR/app && docker compose down --remove-orphans 2>/dev/null || true"
remote "$ROOK_HOST" "cd $ROOK_SERVING_DIR/app && docker compose up -d --build"
echo "  ✓ rook-cluster deployed (API at http://$ROOK_HOST:$ROOK_API_PORT)"
echo ""

# -------------------------------------------------------
# Summary
# -------------------------------------------------------
echo "============================================="
echo " Deployment Complete!"
echo "============================================="
echo ""
echo " Services:"
echo "   MLflow UI:        http://$QUEEN_HOST:$MLFLOW_PORT"
echo "   Pawn Status API:  http://$PAWN_HOST:$PAWN_API_PORT/health"
echo "   Knight Status API:http://$KNIGHT_HOST:$KNIGHT_API_PORT/health"
echo "   Rook Predict API: http://$ROOK_HOST:$ROOK_API_PORT/docs"
echo "   Queen Dashboard:  http://$QUEEN_HOST:$QUEEN_API_PORT/health"
echo ""
echo " Run a health check:  bash shared/healthcheck.sh"
echo " Trigger a pipeline:  ssh $CLUSTER_USER@$QUEEN_HOST 'cd $QUEEN_ORCHESTRATION_DIR/app && docker compose exec orchestrator python src/pipeline_runner.py'"
echo "============================================="
