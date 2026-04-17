"""Backup and restore vault files to/from a portable archive."""
from __future__ import annotations

import base64
import json
import time
from pathlib import Path

from envault.vault import load_vault, save_vault, VaultError


class BackupError(Exception):
    pass


def create_backup(vault_path: Path) -> str:
    """Serialize the vault to a portable base64-encoded JSON string."""
    if not vault_path.exists():
        raise BackupError(f"Vault not found: {vault_path}")
    raw = vault_path.read_bytes()
    bundle = {
        "version": 1,
        "created_at": time.time(),
        "vault_name": vault_path.stem,
        "data": base64.b64encode(raw).decode(),
    }
    return json.dumps(bundle)


def restore_backup(bundle_str: str, dest_path: Path, overwrite: bool = False) -> Path:
    """Restore a vault from a backup bundle string."""
    try:
        bundle = json.loads(bundle_str)
    except json.JSONDecodeError as exc:
        raise BackupError(f"Invalid backup bundle: {exc}") from exc

    if bundle.get("version") != 1:
        raise BackupError("Unsupported backup version")

    if dest_path.exists() and not overwrite:
        raise BackupError(f"Destination already exists: {dest_path}. Use overwrite=True.")

    try:
        data = base64.b64decode(bundle["data"])
    except Exception as exc:
        raise BackupError(f"Failed to decode backup data: {exc}") from exc

    dest_path.write_bytes(data)
    return dest_path


def backup_info(bundle_str: str) -> dict:
    """Return metadata from a backup bundle without restoring it."""
    try:
        bundle = json.loads(bundle_str)
    except json.JSONDecodeError as exc:
        raise BackupError(f"Invalid backup bundle: {exc}") from exc
    return {
        "version": bundle.get("version"),
        "vault_name": bundle.get("vault_name"),
        "created_at": bundle.get("created_at"),
    }
