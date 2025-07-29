from __future__ import annotations
from typing import Dict
from pathlib import Path
import configparser
import os

import typer

try:
    import boto3
    from botocore.exceptions import ClientError  # type: ignore
except Exception:  # pragma: no cover - optional deps
    boto3 = None  # type: ignore
    ClientError = Exception  # type: ignore

from .. import auth_cache


def whoami(env: Dict) -> str:
    """Return a short identity string."""
    key = os.environ.get("AWS_ACCESS_KEY_ID")
    if key:
        return f"AWS access key: {key}"
    profile = env.get("profile")
    if profile:
        return f"AWS profile: {profile}"
    return "AWS credentials not found"


def _profile_name(env: Dict) -> str:
    return env.get("profile") or env.get("name") or "default"


def is_authenticated(env: Dict) -> bool:
    if boto3 is None:
        return False
    profile = _profile_name(env)
    if auth_cache.get(f"aws:{profile}"):
        return True
    try:
        session = boto3.Session(profile_name=profile)
        sts = session.client("sts")
        sts.get_caller_identity()
        auth_cache.set(f"aws:{profile}", True)
        return True
    except Exception:
        return False


def prompt_and_authenticate(env: Dict) -> None:
    if boto3 is None:
        raise RuntimeError("boto3 not available")
    if is_authenticated(env):
        return
    profile = _profile_name(env)
    typer.echo("AWS credentials not found. Enter access details:")
    access_key = typer.prompt("Access key ID")
    secret_key = typer.prompt("Secret access key", hide_input=True)
    cfg_file = Path.home() / ".aws" / "credentials"
    parser = configparser.RawConfigParser()
    if cfg_file.exists():
        parser.read(cfg_file)
    if not parser.has_section(profile):
        parser.add_section(profile)
    parser.set(profile, "aws_access_key_id", access_key)
    parser.set(profile, "aws_secret_access_key", secret_key)
    cfg_file.parent.mkdir(parents=True, exist_ok=True)
    with cfg_file.open("w") as fh:
        parser.write(fh)
    session = boto3.Session(
        aws_access_key_id=access_key, aws_secret_access_key=secret_key
    )
    try:
        session.client("sts").get_caller_identity()
    except Exception as exc:
        raise RuntimeError(f"AWS auth failed: {exc}")
    auth_cache.set(f"aws:{profile}", True)
