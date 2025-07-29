from __future__ import annotations
from typing import Dict
import os

def whoami(env: Dict) -> str:
    """Return a short identity string."""
    key = os.environ.get("AWS_ACCESS_KEY_ID")
    if key:
        return f"AWS access key: {key}"
    return "AWS credentials not found"
