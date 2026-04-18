"""Sort vault secrets by key, optionally grouped by prefix."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from envault.vault import load_vault, save_vault, get_secret, set_secret, list_secrets, VaultError


class SortError(Exception):
    pass


@dataclass
class SortResult:
    vault_path: str
    original_order: list[str]
    sorted_order: list[str]
    group_by_prefix: bool = False

    def __str__(self) -> str:
        changed = self.original_order != self.sorted_order
        status = "reordered" if changed else "already sorted"
        return f"Vault '{self.vault_path}' {status} ({len(self.sorted_order)} keys)"


def _prefix(key: str) -> str:
    """Return the prefix of a key (part before first underscore)."""
    return key.split("_")[0] if "_" in key else key


def sort_vault(
    vault_path: str,
    passphrase: str,
    *,
    group_by_prefix: bool = False,
    reverse: bool = False,
) -> SortResult:
    """Sort all secrets in the vault alphabetically by key.

    Args:
        vault_path: Path to the vault file.
        passphrase: Vault passphrase.
        group_by_prefix: If True, sort within prefix groups (e.g. DB_*, APP_*).
        reverse: If True, sort in descending order.

    Returns:
        SortResult describing what changed.
    """
    vault = load_vault(vault_path)
    keys = list_secrets(vault)
    original_order = list(keys)

    if group_by_prefix:
        sorted_keys = sorted(keys, key=lambda k: (_prefix(k), k), reverse=reverse)
    else:
        sorted_keys = sorted(keys, reverse=reverse)

    # Re-insert secrets in new order by rebuilding the secrets dict
    secrets_snapshot = {k: get_secret(vault, k, passphrase) for k in keys}

    # Clear and re-set in sorted order
    vault["secrets"] = {}
    for k in sorted_keys:
        set_secret(vault, k, secrets_snapshot[k], passphrase)

    save_vault(vault_path, vault)

    return SortResult(
        vault_path=vault_path,
        original_order=original_order,
        sorted_order=sorted_keys,
        group_by_prefix=group_by_prefix,
    )


def is_sorted(vault_path: str, passphrase: str, *, group_by_prefix: bool = False) -> bool:
    """Return True if vault keys are already in sorted order."""
    vault = load_vault(vault_path)
    keys = list_secrets(vault)
    if group_by_prefix:
        expected = sorted(keys, key=lambda k: (_prefix(k), k))
    else:
        expected = sorted(keys)
    return keys == expected
