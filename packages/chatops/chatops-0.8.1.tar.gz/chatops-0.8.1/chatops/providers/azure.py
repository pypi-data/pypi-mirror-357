from __future__ import annotations
from typing import Dict

try:
    from azure.identity import AzureCliCredential  # type: ignore
    from azure.mgmt.subscription import SubscriptionClient  # type: ignore
except Exception:  # pragma: no cover - optional deps
    AzureCliCredential = None  # type: ignore
    SubscriptionClient = None  # type: ignore


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
