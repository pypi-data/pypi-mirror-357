from __future__ import annotations
from typing import Dict

try:
    from google.cloud import storage  # type: ignore
except Exception:  # pragma: no cover - optional deps
    storage = None  # type: ignore


def whoami(env: Dict) -> str:
    """Return the active GCP project."""
    if storage is None:
        pid = env.get("project_id", "unknown")
        return f"GCP project: {pid}"
    client = storage.Client(project=env.get("project_id"))
    return f"GCP project: {client.project}"
