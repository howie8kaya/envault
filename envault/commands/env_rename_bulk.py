"""Bulk rename secrets in a vault using a prefix replacement or explicit mapping."""

from dataclasses import dataclass, field
from typing import Optional
from envault.vault import load_vault, save_vault, get_secret, set_secret, delete_secret, VaultError


class BulkRenameError(Exception):
    pass


@dataclass
class BulkRenameResult:
    renamed: list[tuple[str, str]] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        lines = []
        for old, new in self.renamed:
            lines.append(f"  {old} -> {new}")
        for key in self.skipped:
            lines.append(f"  SKIP {key} (target exists)")
        return "\n".join(lines) if lines else "  (no changes)"


def bulk_rename_by_prefix(
    vault_path: str,
    passphrase: str,
    old_prefix: str,
    new_prefix: str,
    overwrite: bool = False,
) -> BulkRenameResult:
    """Rename all keys that start with old_prefix by replacing it with new_prefix."""
    data = load_vault(vault_path, passphrase)
    keys = list(data["secrets"].keys())
    result = BulkRenameResult()

    for key in keys:
        if not key.startswith(old_prefix):
            continue
        new_key = new_prefix + key[len(old_prefix):]
        if new_key in data["secrets"] and not overwrite:
            result.skipped.append(key)
            continue
        value = get_secret(vault_path, passphrase, key)
        set_secret(vault_path, passphrase, new_key, value)
        delete_secret(vault_path, passphrase, key)
        result.renamed.append((key, new_key))

    return result


def bulk_rename_by_map(
    vault_path: str,
    passphrase: str,
    mapping: dict[str, str],
    overwrite: bool = False,
) -> BulkRenameResult:
    """Rename keys according to an explicit {old: new} mapping."""
    result = BulkRenameResult()

    for old_key, new_key in mapping.items():
        try:
            value = get_secret(vault_path, passphrase, old_key)
        except VaultError:
            raise BulkRenameError(f"Key not found: {old_key}")
        data = load_vault(vault_path, passphrase)
        if new_key in data["secrets"] and not overwrite:
            result.skipped.append(old_key)
            continue
        set_secret(vault_path, passphrase, new_key, value)
        delete_secret(vault_path, passphrase, old_key)
        result.renamed.append((old_key, new_key))

    return result
