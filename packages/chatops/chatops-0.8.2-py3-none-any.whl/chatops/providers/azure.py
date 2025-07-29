from __future__ import annotations
from typing import Dict

import typer

try:
    from azure.identity import (
        AzureCliCredential,
        DeviceCodeCredential,
        DefaultAzureCredential,
    )  # type: ignore
    from azure.mgmt.subscription import SubscriptionClient  # type: ignore
except Exception:  # pragma: no cover - optional deps
    AzureCliCredential = None  # type: ignore
    DeviceCodeCredential = None  # type: ignore
    DefaultAzureCredential = None  # type: ignore
    SubscriptionClient = None  # type: ignore

from .. import auth_cache


def whoami(env: Dict) -> str:
    """Return Azure tenant ID."""
    if AzureCliCredential is None or SubscriptionClient is None:
        tid = env.get("tenant_id", "unknown")
        return f"Azure tenant: {tid}"
    cred = AzureCliCredential()
    sub_client = SubscriptionClient(cred)
    tenant = next(sub_client.tenants.list())
    tid = str(getattr(tenant, "tenant_id", ""))
    return f"Azure tenant: {tid}"


def is_authenticated(env: Dict) -> bool:
    if DefaultAzureCredential is None:
        return False
    if auth_cache.get("azure"):
        return True
    try:
        cred = DefaultAzureCredential(exclude_interactive_browser_credential=False)
        cred.get_token("https://management.azure.com/.default")
        auth_cache.set("azure", True)
        return True
    except Exception:
        return False


def prompt_and_authenticate(env: Dict) -> None:
    if DefaultAzureCredential is None or DeviceCodeCredential is None:
        raise RuntimeError("azure.identity not available")
    if is_authenticated(env):
        return
    typer.echo("Opening browser to log in with device code...")
    cred = DeviceCodeCredential(tenant_id=env.get("tenant_id"))
    try:
        cred.get_token("https://management.azure.com/.default")
    except Exception as exc:
        raise RuntimeError(f"Azure login failed: {exc}")
    auth_cache.set("azure", True)

