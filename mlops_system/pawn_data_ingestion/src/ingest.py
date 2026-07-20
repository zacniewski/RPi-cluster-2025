"""
ingest.py — Main data ingestion script for pawn-cluster.

Supports three source types:
  - demo_iris : loads the Iris dataset from scikit-learn (default for testing)
  - csv_file  : reads a CSV from a local path
  - api       : fetches JSON from a remote URL and converts to DataFrame

After loading, the raw data is saved, validated, and the cleaned version is
written to the processed directory. Optionally pushes the result to
knight-cluster via rsync.

Usage:
    python src/ingest.py                        # use config defaults
    python src/ingest.py --push                  # also rsync to knight
    python src/ingest.py --source demo_iris      # override source type
"""

from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yaml
from sklearn.datasets import load_iris

from validate import validate_dataframe

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("ingest")

CONFIG_PATH = Path("/app/config/ingestion_config.yaml")
RULES_PATH = Path("/app/config/validation_rules.yaml")


def load_config() -> dict:
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


def ingest_demo_iris() -> pd.DataFrame:
    """Load the Iris dataset as a pandas DataFrame."""
    iris = load_iris()
    df = pd.DataFrame(iris.data, columns=[
        "sepal_length", "sepal_width", "petal_length", "petal_width",
    ])
    df["target"] = iris.target
    logger.info("Loaded demo Iris dataset: %d rows, %d columns", len(df), len(df.columns))
    return df


def ingest_csv(path: str) -> pd.DataFrame:
    """Load a CSV file into a DataFrame."""
    df = pd.read_csv(path)
    logger.info("Loaded CSV from %s: %d rows, %d columns", path, len(df), len(df.columns))
    return df


def ingest_api(url: str, headers: dict | None = None) -> pd.DataFrame:
    """Fetch JSON data from an API endpoint and convert to DataFrame."""
    import urllib.request

    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode())
    df = pd.DataFrame(data)
    logger.info("Fetched from API %s: %d rows, %d columns", url, len(df), len(df.columns))
    return df


def save_raw(df: pd.DataFrame, raw_dir: Path, ts: str) -> Path:
    raw_dir.mkdir(parents=True, exist_ok=True)
    path = raw_dir / f"raw_{ts}.csv"
    df.to_csv(path, index=False)
    logger.info("Saved raw data to %s", path)
    return path


def save_processed(df: pd.DataFrame, processed_dir: Path, ts: str) -> Path:
    processed_dir.mkdir(parents=True, exist_ok=True)
    path = processed_dir / f"dataset_{ts}.csv"
    df.to_csv(path, index=False)
    # Also write a "latest" symlink for easy access
    latest = processed_dir / "latest.csv"
    latest.unlink(missing_ok=True)
    latest.symlink_to(path.name)
    logger.info("Saved processed data to %s (latest → %s)", path, path.name)
    return path


def push_to_knight(processed_path: Path, cfg: dict) -> None:
    """Rsync the processed dataset to knight-cluster."""
    dest = f"{cfg['knight_user']}@{cfg['knight_host']}:{cfg['knight_data_dir']}/"
    cmd = [
        "rsync", "-az", "-e", "ssh -o StrictHostKeyChecking=no",
        str(processed_path), dest,
    ]
    logger.info("Pushing to knight-cluster: %s", " ".join(cmd))
    subprocess.run(cmd, check=True)
    # Also push the latest symlink target
    latest = processed_path.parent / "latest.csv"
    if latest.exists():
        subprocess.run(
            ["rsync", "-az", "-e", "ssh -o StrictHostKeyChecking=no",
             str(latest), dest],
            check=True,
        )
    logger.info("Push complete.")


def save_log(log_dir: Path, ts: str, status: str, details: str) -> None:
    log_dir.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": ts,
        "status": status,
        "details": details,
    }
    log_path = log_dir / "ingestion_log.jsonl"
    with open(log_path, "a") as f:
        f.write(json.dumps(entry) + "\n")


def run(source_override: str | None = None, push: bool = False) -> dict:
    """Execute the full ingestion pipeline. Returns a status dict."""
    cfg = load_config()
    ts = datetime.now(timezone.utc).strftime(cfg.get("timestamp_format", "%Y%m%d_%H%M%S"))
    source_type = source_override or cfg["source_type"]

    raw_dir = Path(cfg["raw_dir"])
    processed_dir = Path(cfg["processed_dir"])
    log_dir = Path(cfg["log_dir"])

    # 1. Ingest
    logger.info("Starting ingestion (source_type=%s)", source_type)
    if source_type == "demo_iris":
        df = ingest_demo_iris()
    elif source_type == "csv_file":
        df = ingest_csv(cfg["csv_path"])
    elif source_type == "api":
        df = ingest_api(cfg["api_url"], cfg.get("api_headers"))
    else:
        raise ValueError(f"Unknown source_type: {source_type}")

    # 2. Save raw
    save_raw(df, raw_dir, ts)

    # 3. Validate
    rules = yaml.safe_load(open(RULES_PATH))
    ok, report = validate_dataframe(df, rules)
    if not ok:
        logger.error("Validation FAILED:\n%s", report)
        save_log(log_dir, ts, "FAILED", report)
        return {"status": "failed", "timestamp": ts, "report": report}

    logger.info("Validation PASSED")

    # 4. Save processed
    processed_path = save_processed(df, processed_dir, ts)

    # 5. Optionally push to knight
    if push:
        try:
            push_to_knight(processed_path, cfg)
        except subprocess.CalledProcessError as exc:
            logger.error("Push to knight-cluster failed: %s", exc)
            save_log(log_dir, ts, "PUSH_FAILED", str(exc))
            return {"status": "push_failed", "timestamp": ts, "report": str(exc)}

    save_log(log_dir, ts, "SUCCESS", f"rows={len(df)}, cols={len(df.columns)}")
    return {"status": "success", "timestamp": ts, "rows": len(df), "columns": len(df.columns)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run data ingestion pipeline")
    parser.add_argument("--source", type=str, default=None, help="Override source_type")
    parser.add_argument("--push", action="store_true", help="Push processed data to knight-cluster")
    args = parser.parse_args()

    result = run(source_override=args.source, push=args.push)
    logger.info("Ingestion result: %s", json.dumps(result, indent=2))
    if result["status"] != "success":
        sys.exit(1)


if __name__ == "__main__":
    main()
