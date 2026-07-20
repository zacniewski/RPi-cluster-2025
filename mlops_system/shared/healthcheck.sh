#!/usr/bin/env bash
# =============================================================================
# healthcheck.sh — Check the health of all MLOps cluster services
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/config.env"

if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "ERROR: $CONFIG_FILE not found."
    exit 1
fi

source "$CONFIG_FILE"

check_service() {
    local name="$1"
    local url="$2"
    local status

    if status=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 3 "$url" 2>/dev/null); then
        if [[ "$status" == "200" ]]; then
            echo "  ✓ $name — OK ($url)"
        else
            echo "  ✗ $name — HTTP $status ($url)"
        fi
    else
        echo "  ✗ $name — UNREACHABLE ($url)"
    fi
}

echo "============================================="
echo " MLOps Cluster Health Check"
echo "============================================="
echo ""

echo "Services:"
check_service "MLflow UI"         "http://$QUEEN_HOST:$MLFLOW_PORT/"
check_service "Pawn Status API"   "http://$PAWN_HOST:$PAWN_API_PORT/health"
check_service "Knight Status API" "http://$KNIGHT_HOST:$KNIGHT_API_PORT/health"
check_service "Rook Predict API"  "http://$ROOK_HOST:$ROOK_API_PORT/health"
check_service "Queen Dashboard"   "http://$QUEEN_HOST:$QUEEN_API_PORT/health"

echo ""
echo "Node SSH connectivity:"
for node in "$PAWN_HOST" "$KNIGHT_HOST" "$ROOK_HOST" "$QUEEN_HOST"; do
    if ssh -o StrictHostKeyChecking=no -o ConnectTimeout=3 "${CLUSTER_USER}@${node}" "echo ok" &>/dev/null; then
        echo "  ✓ $node — SSH OK"
    else
        echo "  ✗ $node — SSH FAILED"
    fi
done

echo ""
echo "Docker status on each node:"
for node in "$PAWN_HOST" "$KNIGHT_HOST" "$ROOK_HOST" "$QUEEN_HOST"; do
    containers=$(ssh -o StrictHostKeyChecking=no -o ConnectTimeout=3 "${CLUSTER_USER}@${node}" \
        "docker ps --format '{{.Names}} ({{.Status}})'" 2>/dev/null || echo "UNREACHABLE")
    echo "  $node:"
    echo "$containers" | sed 's/^/    /'
done

echo ""
echo "============================================="
