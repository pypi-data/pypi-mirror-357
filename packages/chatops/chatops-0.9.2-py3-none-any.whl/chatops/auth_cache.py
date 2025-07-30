from __future__ import annotations
from pathlib import Path
from typing import Dict

try:
    import yaml
except Exception:  # pragma: no cover - optional dependency
    yaml = None  # type: ignore

AUTH_CACHE_FILE = Path.home() / ".chatops" / ".auth_cache.yaml"


def _load() -> Dict:
    if not AUTH_CACHE_FILE.exists():
        return {}
    text = AUTH_CACHE_FILE.read_text()
    if yaml is None:
        # naive parse
        data: Dict[str, bool] = {}
        for line in text.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                data[k.strip()] = v.strip() == "true"
        return data
    try:
        return yaml.safe_load(text) or {}
    except Exception:
        return {}


def _save(data: Dict[str, bool]) -> None:
    AUTH_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    if yaml is None:
        text = "\n".join(f"{k}: {'true' if v else 'false'}" for k, v in data.items())
        AUTH_CACHE_FILE.write_text(text)
    else:
        AUTH_CACHE_FILE.write_text(yaml.safe_dump(data))


def get(key: str) -> bool:
    return _load().get(key, False)


def set(key: str, value: bool) -> None:
    data = _load()
    data[key] = value
    _save(data)
