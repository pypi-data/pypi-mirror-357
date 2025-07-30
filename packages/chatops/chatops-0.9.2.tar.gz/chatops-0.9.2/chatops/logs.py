from __future__ import annotations
import time
import importlib
import typer
from rich.console import Console
from rich.table import Table
from rich.live import Live
from .utils import log_command, time_command
from . import env as env_mod

app = typer.Typer(help="Logging related commands", invoke_without_command=True)


def _provider_module(ctx: typer.Context):
    env_cfg = env_mod.load_env(ctx.obj.get("env_override"))
    provider = env_cfg.get("provider")
    return importlib.import_module(f".providers.{provider}", __package__)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    service: str = typer.Argument(None, help="Service name"),
    lines: int = typer.Option(50, "--lines", help="Number of log lines"),
) -> None:
    """Tail logs for ``service`` if no subcommand is specified."""
    if ctx.invoked_subcommand is None:
        if not service:
            typer.echo("Provide SERVICE or see --help")
            raise typer.Exit(1)
        env_mod.load_env(ctx.obj.get("env_override"))
        tail(ctx, service, lines)


@time_command
@log_command
@app.command()
def live(ctx: typer.Context, service: str = typer.Argument(..., help="Service name")):
    """Simulate live logs for a service."""
    _provider_module(ctx)
    console = Console()
    with Live(refresh_per_second=4) as live_obj:
        for i in range(5):
            live_obj.update(Table().add_column("log").add_row(f"{service} log line {i}"))
            time.sleep(0.5)
    console.print("[green]Streaming ended[/green]")


@time_command
@log_command
@app.command()
def grep(
    ctx: typer.Context, pattern: str = typer.Argument(..., help="Text to search")
):
    """Search mock logs."""
    _provider_module(ctx)
    logs = ["error starting service", "service ready", "warning: high memory"]
    matches = [l for l in logs if pattern in l]
    table = Table(title="Matches")
    table.add_column("Line")
    for m in matches:
        table.add_row(m)
    Console().print(table)


@time_command
@log_command
@app.command()
def tail(
    ctx: typer.Context,
    service: str = typer.Argument(..., help="Service name"),
    lines: int = typer.Option(50, "--lines", help="Number of log lines"),
):
    """Tail provider-specific log output."""
    mod = _provider_module(ctx)
    env_cfg = env_mod.load_env(ctx.obj.get("env_override"))
    if hasattr(mod, "tail_logs"):
        logs = mod.tail_logs(env_cfg, service, lines)
    else:
        logs = [f"log line {i}" for i in range(lines)]
    table = Table(title=f"{service} logs")
    table.add_column("Line")
    for line in logs:
        table.add_row(line)
    Console().print(table)

