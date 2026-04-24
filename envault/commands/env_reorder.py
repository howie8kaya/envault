"""Reorder secrets in a vault according to a given key order or sort strategy."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from envault.vault import VaultError, load_vault, save_vault


class ReorderError(Exception):
    pass


@dataclass
class ReorderResult:
    vault_path: str
    original_order: List[str]
    new_order: List[str]
    moved: int

    def __str__(self) -> str:
        return (
            f"Reordered {self.moved} key(s) in '{self.vault_path}'\n"
            f"New order: {', '.join(self.new_order)}"
        )


def reorder_vault(
    vault_path: str,
    passphrase: str,
    key_order: Optional[List[str]] = None,
    alphabetical: bool = False,
    reverse: bool = False,
) -> ReorderResult:
    """Reorder vault secrets by an explicit key list or alphabetically."""
    if key_order is None and not alphabetical:
        raise ReorderError("Provide key_order or set alphabetical=True.")

    data = load_vault(vault_path, passphrase)
    secrets: dict = data.get("secrets", {})
    original_order = list(secrets.keys())

    if alphabetical:
        new_keys = sorted(secrets.keys(), reverse=reverse)
    else:
        unknown = [k for k in key_order if k not in secrets]
        if unknown:
            raise ReorderError(f"Unknown key(s): {', '.join(unknown)}")
        trailing = [k for k in secrets if k not in key_order]
        new_keys = key_order + trailing
        if reverse:
            new_keys = list(reversed(new_keys))

    reordered = {k: secrets[k] for k in new_keys}
    moved = sum(1 for i, k in enumerate(new_keys) if i >= len(original_order) or original_order[i] != k)

    data["secrets"] = reordered
    save_vault(vault_path, passphrase, data)

    return ReorderResult(
        vault_path=vault_path,
        original_order=original_order,
        new_order=new_keys,
        moved=moved,
    )


def current_order(vault_path: str, passphrase: str) -> List[str]:
    """Return the current key order in the vault."""
    data = load_vault(vault_path, passphrase)
    return list(data.get("secrets", {}).keys())
