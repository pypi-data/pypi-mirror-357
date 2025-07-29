from __future__ import annotations
import os
import subprocess
import typer
from rich.console import Console
from rich.table import Table
from .utils import log_command, time_command
from . import env as env_mod
from .providers import aws, azure, gcp, docker

app = typer.Typer(help="Cloud provider utilities")


@app.command()
@time_command
@log_command
def whoami(
    ctx: typer.Context,
    provider: str = typer.Option(None, "--provider", help="aws|azure|gcp"),
):
    """Show identity information for the given cloud provider."""
    console = Console()
    env_cfg = env_mod.get_env(ctx.obj.get("env_override"))
    if provider is None and env_cfg:
        provider = env_cfg.get("provider")
    if provider is None:
        console.print("[red]No active environment[/red]")
        raise typer.Exit(1)
    if provider == "aws":
        identity = aws.whoami(env_cfg or {})
        console.print(identity)
    elif provider == "azure":
        identity = azure.whoami(env_cfg or {})
        console.print(identity)
    elif provider == "gcp":
        identity = gcp.whoami(env_cfg or {})
        console.print(identity)
    elif provider == "docker":
        identity = docker.whoami(env_cfg or {})
        console.print(identity)
    else:
        console.print("[red]Unknown provider[/red]")


cost_app = typer.Typer(help="Cost commands")
app.add_typer(cost_app, name="cost")


@cost_app.command("top-services")
@time_command
@log_command
def top_services(
    ctx: typer.Context,
    provider: str = typer.Option(None, "--provider", help="aws|azure|gcp"),
):
    """Show top services by cost."""
    if provider is None:
        env_cfg = env_mod.get_env(ctx.obj.get("env_override"))
        if not env_cfg:
            Console().print("[red]No active environment[/red]")
            raise typer.Exit(1)
        provider = env_cfg.get("provider")
    table = Table(title="Top Services")
    table.add_column("Service")
    table.add_column("Cost", justify="right")
    for i in range(1, 4):
        table.add_row(f"Service{i}", f"${100*i:.2f}")
    Console().print(table)


@app.command()
@time_command
@log_command
def deploy(
    ctx: typer.Context,
    service: str = typer.Option(..., "--service", help="Service name"),
    region: str = typer.Option("us-east-1", "--region", help="Target region"),
    provider: str = typer.Option(None, "--provider", help="aws|azure|gcp"),
):
    """Simulate deploying a cloud service."""
    if provider is None:
        env_cfg = env_mod.get_env(ctx.obj.get("env_override"))
        if not env_cfg:
            Console().print("[red]No active environment[/red]")
            raise typer.Exit(1)
        provider = env_cfg.get("provider")
    Console().print(f"Deploying {service} to {provider} in {region}...")

