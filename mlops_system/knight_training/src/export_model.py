"""
export_model.py — Push trained model artifacts to rook-cluster via rsync.
"""

from __future__ import annotations

import logging
import subprocess
from pathlib import Path

logger = logging.getLogger("export_model")


def push_to_rook(model_path: Path, cfg: dict) -> None:
    """Rsync the model file and latest symlink to rook-cluster."""
    dest = f"{cfg['rook_user']}@{cfg['rook_host']}:{cfg['rook_model_dir']}/"
    cmd = [
        "rsync", "-az", "-e", "ssh -o StrictHostKeyChecking=no",
        str(model_path), dest,
    ]
    logger.info("Pushing model to rook-cluster: %s", " ".join(cmd))
    subprocess.run(cmd, check=True)

    # Also push the latest symlink
    parent = model_path.parent
    for symlink in parent.glob("latest.*"):
        subprocess.run(
            ["rsync", "-az", "--links", "-e", "ssh -o StrictHostKeyChecking=no",
             str(symlink), dest],
            check=True,
        )
    logger.info("Model push complete.")
