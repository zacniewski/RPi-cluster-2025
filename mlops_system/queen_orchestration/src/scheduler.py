"""
scheduler.py — APScheduler-based pipeline scheduler for queen-cluster.

Runs the full MLOps pipeline on a configurable interval.
Designed to be started as a background thread from the dashboard API.
"""

from __future__ import annotations

import logging
from pathlib import Path

import yaml
from apscheduler.schedulers.background import BackgroundScheduler

from pipeline_runner import run_pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("scheduler")

CONFIG_PATH = Path("/app/config/pipeline_config.yaml")

_scheduler: BackgroundScheduler | None = None


def _load_interval() -> int:
    with open(CONFIG_PATH) as f:
        cfg = yaml.safe_load(f)
    return cfg.get("schedule_interval_hours", 6)


def _scheduled_run() -> None:
    """Callback executed by APScheduler."""
    logger.info("Scheduled pipeline run starting...")
    result = run_pipeline()
    logger.info("Scheduled pipeline run finished: %s", result.get("status"))


def start_scheduler() -> BackgroundScheduler:
    """Start the background scheduler. Idempotent — safe to call multiple times."""
    global _scheduler
    if _scheduler is not None and _scheduler.running:
        logger.info("Scheduler already running.")
        return _scheduler

    interval_hours = _load_interval()
    _scheduler = BackgroundScheduler()
    _scheduler.add_job(
        _scheduled_run,
        trigger="interval",
        hours=interval_hours,
        id="mlops_pipeline",
        replace_existing=True,
    )
    _scheduler.start()
    logger.info("Scheduler started — pipeline runs every %d hour(s).", interval_hours)
    return _scheduler


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped.")
    _scheduler = None


def is_running() -> bool:
    return _scheduler is not None and _scheduler.running
