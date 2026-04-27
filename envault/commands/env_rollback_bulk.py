"""Bulk rollback multiple vault secrets to their latest recorded versions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envault.vault import load_vault, save_vault
from envault.commands.env_version import _version_meta
from envault.commands.env_rollback import RollbackError


@dataclass
class BulkRollbackResult:
    rolled_back: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    errors: Dict[str, str] = field(default_factory=dict)

    def __str__(self) -> str:
        lines = []
        if self.rolled_back:
            lines.append(f"Rolled back: {', '.join(self.rolled_back)}")
        if self.skipped:
            lines.append(f"Skipped (no history): {', '.join(self.skipped)}")
        if self.errors:
            for k, msg in self.errors.items():
                lines.append(f"Error [{k}]: {msg}")
        return "\n".join(lines) if lines else "Nothing to roll back."


def bulk_rollback(
    vault_path: str,
    passphrase: str,
    keys: Optional[List[str]] = None,
    target_version: int = 1,
) -> BulkRollbackResult:
    """Roll back multiple keys to a given version in a single vault write.

    Args:
        vault_path: Path to the vault file.
        passphrase: Vault passphrase.
        keys: List of keys to roll back. If None, all keys with history are used.
        target_version: Version number to restore for each key.

    Returns:
        BulkRollbackResult summarising what was changed.
    """
    vault = load_vault(vault_path, passphrase)
    meta = _version_meta(vault)

    candidate_keys = keys if keys is not None else list(vault.keys())
    result = BulkRollbackResult()

    for key in candidate_keys:
        if key not in vault:
            result.errors[key] = f"Key '{key}' not found in vault."
            continue

        history = meta.get(key, [])
        if not history:
            result.skipped.append(key)
            continue

        entry = next((e for e in history if e["version"] == target_version), None)
        if entry is None:
            available = [e["version"] for e in history]
            result.errors[key] = (
                f"Version {target_version} not found. Available: {available}"
            )
            continue

        vault[key] = entry["value"]
        result.rolled_back.append(key)

    if result.rolled_back:
        save_vault(vault_path, passphrase, vault)

    return result
