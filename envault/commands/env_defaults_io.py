"""env_defaults_io.py — save/load a defaults manifest (JSON) alongside a vault."""
from __future__ import annotations

import json
from pathlib import Path


class DefaultsIOError(Exception):
    pass


def _defaults_path(vault_path: Path) -> Path:
    return vault_path.with_suffix(".defaults.json")


def save_defaults_manifest(vault_path: Path, defaults: dict[str, str]) -> Path:
    """Persist a defaults dict as JSON next to the vault file."""
    if not isinstance(defaults, dict):
        raise DefaultsIOError("defaults must be a dict")
    path = _defaults_path(vault_path)
    path.write_text(json.dumps(defaults, indent=2), encoding="utf-8")
    return path


def load_defaults_manifest(vault_path: Path) -> dict[str, str]:
    """Load a previously saved defaults manifest."""
    path = _defaults_path(vault_path)
    if not path.exists():
        raise DefaultsIOError(f"No defaults manifest found at {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise DefaultsIOError(f"Invalid JSON in defaults manifest: {exc}") from exc
    if not isinstance(data, dict):
        raise DefaultsIOError("Defaults manifest must be a JSON object")
    return data


def delete_defaults_manifest(vault_path: Path) -> bool:
    """Remove the defaults manifest if it exists. Returns True if deleted."""
    path = _defaults_path(vault_path)
    if path.exists():
        path.unlink()
        return True
    return False
