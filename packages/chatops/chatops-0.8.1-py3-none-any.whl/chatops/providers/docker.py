from __future__ import annotations
from typing import Dict
import os


def whoami(env: Dict) -> str:
    """Return Docker host information."""
    socket = env.get("socket", "/var/run/docker.sock")
    return f"Docker socket: {os.path.basename(socket)}"
