from __future__ import annotations
from typing import Dict
from pathlib import Path

import typer

try:
    from google.cloud import storage  # type: ignore
    from google.oauth2 import service_account  # type: ignore
    import google.auth  # type: ignore
except Exception:  # pragma: no cover - optional deps
    storage = None  # type: ignore
    service_account = None  # type: ignore
    google = None  # type: ignore

from .. import auth_cache


def whoami(env: Dict) -> str:
    """Return the active GCP project."""
    if storage is None:
        pid = env.get("project_id", "unknown")
        return f"GCP project: {pid}"
    client = storage.Client(project=env.get("project_id"))
    return f"GCP project: {client.project}"


def is_authenticated(env: Dict) -> bool:
    if google is None:
        return False
    proj = env.get("project_id", "default")
    if auth_cache.get(f"gcp:{proj}"):
        return True
    try:
        creds, project = google.auth.default()
        if project:
            auth_cache.set(f"gcp:{project}", True)
            return True
    except Exception:
        return False
    return False


def prompt_and_authenticate(env: Dict) -> None:
    if service_account is None:
        raise RuntimeError("google-auth not available")
    if is_authenticated(env):
        return
    path = typer.prompt("Enter path to service account JSON")
    key_path = Path(path).expanduser()
    try:
        creds = service_account.Credentials.from_service_account_file(str(key_path))
    except Exception as exc:
        raise RuntimeError(f"GCP credential error: {exc}")
    auth_cache.set(f"gcp:{creds.project_id}", True)
    env["project_id"] = creds.project_id
    env["service_account"] = str(key_path)

