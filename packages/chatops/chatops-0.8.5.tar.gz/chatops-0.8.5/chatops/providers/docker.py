from __future__ import annotations
from typing import Dict
from pathlib import Path
import os

import typer

try:
    import docker  # type: ignore
except Exception:  # pragma: no cover - optional deps
    docker = None  # type: ignore

from .. import auth_cache


def whoami(env: Dict) -> str:
    """Return Docker host information."""
    socket = env.get("socket", "/var/run/docker.sock")
    return f"Docker socket: {os.path.basename(socket)}"


def is_authenticated(env: Dict) -> bool:
    if docker is None:
        return False
    if auth_cache.get("docker"):
        return True
    socket = env.get("socket", "/var/run/docker.sock")
    url = f"unix://{socket}" if not socket.startswith("unix://") else socket
    try:
        client = docker.DockerClient(base_url=url)
        client.ping()
        auth_cache.set("docker", True)
        return True
    except Exception:
        return False


def prompt_and_authenticate(env: Dict) -> None:
    if docker is None:
        raise RuntimeError("docker SDK not available")
    if is_authenticated(env):
        return
    typer.echo("Docker not accessible. Enter Docker host path:")
    host = typer.prompt("Docker host", default=env.get("socket", "/var/run/docker.sock"))
    env["socket"] = host
    url = f"unix://{host}" if not host.startswith("unix://") else host
    try:
        docker.DockerClient(base_url=url).ping()
    except Exception as exc:
        raise RuntimeError(f"Docker auth failed: {exc}")
    auth_cache.set("docker", True)



# Additional utility functions
from typing import List, Tuple


def cost_report(env: Dict) -> List[Tuple[str, float]]:
    """Return dummy cost data."""
    return [("Containers", 50.0)]


def tail_logs(env: Dict, service: str, lines: int) -> List[str]:
    """Return dummy log lines for Docker services."""
    return [f"{service} log {i}" for i in range(lines)]
