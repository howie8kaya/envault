"""Rollback vault secrets to a previous version snapshot."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from envault.vault import VaultError, load_vault, save_vault
from envault.commands.env_version import _version_meta


class RollbackError(Exception):
    pass


@dataclass
class RollbackResult:
    key: str
    rolled_back_to_version: int
    previous_value_preview: str
    reverted_keys: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        keys = ", ".join(self.reverted_keys) if self.reverted_keys else self.key
        return (
            f"Rolled back '{keys}' to version {self.rolled_back_to_version} "
            f"(was: {self.previous_value_preview})"
        )


def rollback_secret(
    vault_path: str,
    passphrase: str,
    key: str,
    target_version: int,
) -> RollbackResult:
    """Rollback a single secret to a specific historical version."""
    vault = load_vault(vault_path, passphrase)

    if key not in vault:
        raise RollbackError(f"Key '{key}' not found in vault.")

    meta = _version_meta(vault)
    history = meta.get(key, [])

    if not history:
        raise RollbackError(f"No version history found for '{key}'.")

    entry = next((e for e in history if e["version"] == target_version), None)
    if entry is None:
        available = [e["version"] for e in history]
        raise RollbackError(
            f"Version {target_version} not found for '{key}'. Available: {available}"
        )

    current_preview = vault[key][:6] + "..." if len(vault[key]) > 6 else vault[key]
    vault[key] = entry["value"]
    save_vault(vault_path, passphrase, vault)

    return RollbackResult(
        key=key,
        rolled_back_to_version=target_version,
        previous_value_preview=current_preview,
        reverted_keys=[key],
    )


def list_rollback_versions(vault_path: str, passphrase: str, key: str) -> List[dict]:
    """List all available versions for a given key."""
    vault = load_vault(vault_path, passphrase)

    if key not in vault:
        raise RollbackError(f"Key '{key}' not found in vault.")

    meta = _version_meta(vault)
    return meta.get(key, [])
