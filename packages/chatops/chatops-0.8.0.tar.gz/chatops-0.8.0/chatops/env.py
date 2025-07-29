from __future__ import annotations

from pathlib import Path
from typing import Optional, Dict
import shutil


SANDBOX_DIR = Path.home() / ".chatops" / "sandboxes"

from rich.console import Console
import typer

from . import config

ACTIVE_FILE = Path.home() / ".chatops" / ".active_env"

app = typer.Typer(help="Environment management")


def _active_name() -> Optional[str]:
    if ACTIVE_FILE.exists():
        return ACTIVE_FILE.read_text().strip() or None
    return None


def active_env() -> Optional[Dict]:
    name = _active_name()
    if name:
        return config.get_env(name)
    return None


def _sandbox_path(name: str) -> Path:
    return SANDBOX_DIR / name


def _setup_sandbox(name: str) -> None:
    path = _sandbox_path(name)
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)
    env_cfg = config.get_env(name) or {}
    provider = env_cfg.get("provider", "unknown")
    (path / "provider").write_text(provider)


def set_active(name: str) -> None:
    config.validate_env(name)
    ACTIVE_FILE.parent.mkdir(parents=True, exist_ok=True)
    ACTIVE_FILE.write_text(name)
    _setup_sandbox(name)


def clear_active() -> None:
    if ACTIVE_FILE.exists():
        ACTIVE_FILE.unlink()


def get_env(override: Optional[str] = None) -> Optional[Dict]:
    if override:
        config.validate_env(override)
        return config.get_env(override)
    return active_env()


@app.command("use")
def use(name: str = typer.Argument(..., help="Environment name")):
    """Activate an environment."""
    try:
        set_active(name)
    except Exception as exc:
        Console().print(f"[red]{exc}[/red]")
        raise typer.Exit(1)
    Console().print(f"Using environment {name}")


@app.command("current")
def current():
    """Show current active environment."""
    name = _active_name()
    if name:
        Console().print(name)
    else:
        Console().print("none")


@app.command("list")
def list_envs():
    """List configured environments."""
    for env in config.environments():
        Console().print(env)


@app.command("exit")
def exit_env():
    """Deactivate current environment."""
    name = _active_name()
    clear_active()
    if name:
        path = _sandbox_path(name)
        if path.exists():
            shutil.rmtree(path)
    Console().print("Environment cleared")

