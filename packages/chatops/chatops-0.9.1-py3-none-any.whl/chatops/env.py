from __future__ import annotations
import importlib

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    yaml = None  # type: ignore

from pathlib import Path
from typing import Optional, Dict
from datetime import datetime
import shutil

def _pretty_path(path: Path) -> str:
    """Return path string with home replaced by ~ for readability."""
    try:
        home = str(Path.home())
        text = str(path)
        if text.startswith(home):
            return text.replace(home, "~", 1)
        return text
    except Exception:
        return str(path)


SANDBOX_DIR = Path.home() / ".chatops" / "sandboxes"

from rich.console import Console
from rich.table import Table
import typer

from . import config

ACTIVE_FILE = Path.home() / ".chatops" / ".active_env"

app = typer.Typer(help="Environment management")


def _load_active() -> Optional[Dict]:
    if not ACTIVE_FILE.exists():
        return None
    text = ACTIVE_FILE.read_text()
    if yaml is None:
        data: Dict[str, str] = {}
        for line in text.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                data[k.strip()] = v.strip()
        return data
    try:
        loaded = yaml.safe_load(text) or {}
        if isinstance(loaded, dict):
            return loaded
    except Exception:
        return None
    return None


def _active_name() -> Optional[str]:
    data = _load_active()
    if data:
        return str(data.get("name")) if data.get("name") else None
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
    env_cfg = config.get_env(name) or {}
    data = {
        "provider": env_cfg.get("provider", "unknown"),
        "name": name,
        "timestamp": datetime.utcnow().isoformat(),
    }
    ACTIVE_FILE.parent.mkdir(parents=True, exist_ok=True)
    if yaml is None:
        text = "\n".join(f"{k}: {v}" for k, v in data.items())
        ACTIVE_FILE.write_text(text)
    else:
        ACTIVE_FILE.write_text(yaml.safe_dump(data))
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
    console = Console()
    cfg_path = _pretty_path(config.CONFIG_FILE)
    if not config.CONFIG_FILE.exists():
        console.print(f"[red]Config file {cfg_path} not found[/red]")
        raise typer.Exit(1)
    env_cfg = config.get_env(name)
    if env_cfg is None:
        console.print(
            f"[red]Environment '{name}' not found in {cfg_path}. Make sure the file exists and is readable[/red]"
        )
        raise typer.Exit(1)
    provider = env_cfg.get("provider", "")
    missing = []
    if provider == "azure":
        for key in ("subscription_id", "tenant_id"):
            if not env_cfg.get(key):
                missing.append(key)
    elif provider == "gcp":
        if not env_cfg.get("project_id"):
            missing.append("project_id")
    if missing:
        console.print(
            f"[red]Environment '{name}' missing required fields: {', '.join(missing)}[/red]"
        )
        raise typer.Exit(1)
    try:
        if provider in {"aws", "azure", "gcp", "docker"}:
            mod = _provider_module(provider)
            if hasattr(mod, "is_authenticated") and not mod.is_authenticated(env_cfg):
                if hasattr(mod, "prompt_and_authenticate"):
                    mod.prompt_and_authenticate(env_cfg)
        set_active(name)
    except Exception as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1)
    console.print(f"Using environment {name}")


@app.command("current")
def current():
    """Show current active environment."""
    data = _load_active()
    if data and data.get("name"):
        Console().print(data["name"])
    else:
        Console().print("none")


@app.command("list")
def list_envs():
    """List configured environments."""
    console = Console()
    envs = config.environments()
    if not envs:
        console.print("No environments configured")
        return
    table = Table(title="Environments")
    table.add_column("Name")
    table.add_column("Provider")
    for name, info in envs.items():
        table.add_row(name, info.get("provider", ""))
    console.print(table)


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
    data = _load_active()
    name = data.get("name") if data else None
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



