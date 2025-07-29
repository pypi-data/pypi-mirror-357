from __future__ import annotations
import importlib

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


def load_env(override: Optional[str] = None) -> Dict:
    """Return env config or raise if unavailable."""
    env_cfg = get_env(override)
    if env_cfg is None:
        raise RuntimeError("No environment selected. Run `chatops env use <env>`." )
    return env_cfg


def provider(override: Optional[str] = None) -> str:
    """Return provider name for active or overridden env."""
    env_cfg = load_env(override)
    return env_cfg.get("provider", "")


def get_env(override: Optional[str] = None) -> Optional[Dict]:
    if override:
        config.validate_env(override)
        return config.get_env(override)
    return active_env()


def _provider_module(name: str):
    return importlib.import_module(f".providers.{name}", __package__)
@app.command("use")
def use(name: str = typer.Argument(..., help="Environment name")):
    """Activate an environment."""
    try:
        env_cfg = config.get_env(name)
        if env_cfg is None:
            raise ValueError(f"Environment {name} not found")
        provider = env_cfg.get("provider")
        if provider in {"aws", "azure", "gcp", "docker"}:
            mod = _provider_module(provider)
            if hasattr(mod, "prompt_and_authenticate"):
                mod.prompt_and_authenticate(env_cfg)
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
@app.command("status")
def status():
    """Show authentication status for active environment."""
    name = _active_name()
    if not name:
        Console().print("none")
        raise typer.Exit(1)
    env_cfg = config.get_env(name) or {}
    provider = env_cfg.get("provider")
    authed = False
    if provider:
        mod = _provider_module(provider)
        if hasattr(mod, "is_authenticated"):
            authed = mod.is_authenticated(env_cfg)
    if authed:
        Console().print(f"{name} authenticated")
    else:
        Console().print(f"[red]{name} not authenticated[/red]")



