"""
pipeline_runner.py — End-to-end pipeline orchestrator for queen-cluster.

Executes the full MLOps pipeline by calling HTTP endpoints on each node
in sequence: ingest → train → reload model.

Can be run standalone or called from the scheduler / API.

Usage:
    python src/pipeline_runner.py           # run full pipeline once
    python src/pipeline_runner.py --step ingest   # run a single step
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

import httpx
import yaml

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("pipeline")

CONFIG_PATH = Path("/app/config/pipeline_config.yaml")


def load_config() -> dict:
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


def execute_step(step: dict, nodes: dict) -> dict:
    """Execute a single pipeline step by calling the node's HTTP API."""
    node_cfg = nodes[step["node"]]
    base_url = f"http://{node_cfg['host']}:{node_cfg['api_port']}"
    url = f"{base_url}{step['path']}"
    method = step.get("method", "POST").upper()
    timeout = step.get("timeout", 60)
    body = step.get("body", {})

    logger.info("Step '%s': %s %s", step["name"], method, url)

    try:
        with httpx.Client(timeout=timeout) as client:
            if method == "POST":
                resp = client.post(url, json=body)
            else:
                resp = client.get(url)

            resp.raise_for_status()
            result = resp.json()
            logger.info("Step '%s' completed: %s", step["name"], result.get("status", "ok"))
            return {"step": step["name"], "status": "success", "response": result}

    except httpx.HTTPStatusError as exc:
        logger.error("Step '%s' HTTP error: %s %s", step["name"], exc.response.status_code, exc.response.text)
        return {"step": step["name"], "status": "failed", "error": f"HTTP {exc.response.status_code}"}
    except httpx.ConnectError as exc:
        logger.error("Step '%s' connection error: %s", step["name"], exc)
        return {"step": step["name"], "status": "failed", "error": f"Connection failed: {exc}"}
    except Exception as exc:
        logger.error("Step '%s' unexpected error: %s", step["name"], exc)
        return {"step": step["name"], "status": "failed", "error": str(exc)}


def save_run_log(log_dir: Path, ts: str, results: list[dict]) -> None:
    log_dir.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": ts,
        "steps": results,
        "overall_status": "success" if all(r["status"] == "success" for r in results) else "failed",
    }
    log_path = log_dir / "pipeline_log.jsonl"
    with open(log_path, "a") as f:
        f.write(json.dumps(entry) + "\n")
    logger.info("Run log saved to %s", log_path)


def run_pipeline(step_filter: str | None = None) -> dict:
    """Run the full pipeline (or a single step). Returns a summary dict."""
    cfg = load_config()
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    nodes = cfg["nodes"]
    steps = cfg["pipeline_steps"]
    log_dir = Path(cfg.get("log_dir", "/logs"))

    if step_filter:
        steps = [s for s in steps if s["name"] == step_filter]
        if not steps:
            logger.error("No step named '%s' found in config.", step_filter)
            return {"status": "error", "message": f"Unknown step: {step_filter}"}

    results = []
    for step in steps:
        result = execute_step(step, nodes)
        results.append(result)
        if result["status"] != "success":
            logger.warning("Step '%s' failed — stopping pipeline.", step["name"])
            break

    save_run_log(log_dir, ts, results)

    overall = "success" if all(r["status"] == "success" for r in results) else "failed"
    return {"status": overall, "timestamp": ts, "steps": results}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the MLOps pipeline")
    parser.add_argument("--step", type=str, default=None, help="Run a single step by name")
    args = parser.parse_args()

    result = run_pipeline(step_filter=args.step)
    logger.info("Pipeline result: %s", json.dumps(result, indent=2))
    if result["status"] != "success":
        sys.exit(1)


if __name__ == "__main__":
    main()
