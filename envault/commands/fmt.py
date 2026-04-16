"""Format/normalize vault keys (e.g. uppercase, strip whitespace)."""

from dataclasses import dataclass
from typing import List, Optional
from envault.vault import load_vault, save_vault, get_secret, set_secret, delete_secret, VaultError


class FmtError(Exception):
    pass


@dataclass
class FmtChange:
    old_key: str
    new_key: str
    value_changed: bool = False

    def __str__(self) -> str:
        tag = " (value normalized)" if self.value_changed else ""
        return f"{self.old_key} -> {self.new_key}{tag}"


def _normalize_key(key: str) -> str:
    return key.strip().upper().replace("-", "_").replace(" ", "_")


def _normalize_value(value: str) -> str:
    return value.strip()


def fmt_vault(
    vault_path: str,
    passphrase: str,
    keys_only: bool = False,
    dry_run: bool = False,
) -> List[FmtChange]:
    """Normalize key names (and optionally values) in the vault.

    Returns list of changes made (or that would be made if dry_run=True).
    """
    vault = load_vault(vault_path)
    secrets: dict = vault.get("secrets", {})
    changes: List[FmtChange] = []

    for raw_key in list(secrets.keys()):
        new_key = _normalize_key(raw_key)
        old_value = get_secret(vault_path, passphrase, raw_key)
        new_value = old_value if keys_only else _normalize_value(old_value)
        value_changed = new_value != old_value
        key_changed = new_key != raw_key

        if not key_changed and not value_changed:
            continue

        if new_key != raw_key and new_key in secrets and new_key != raw_key:
            raise FmtError(
                f"Cannot rename '{raw_key}' to '{new_key}': key already exists."
            )

        changes.append(FmtChange(old_key=raw_key, new_key=new_key, value_changed=value_changed))

        if not dry_run:
            set_secret(vault_path, passphrase, new_key, new_value)
            if key_changed:
                delete_secret(vault_path, passphrase, raw_key)

    return changes


def format_fmt_results(changes: List[FmtChange]) -> str:
    if not changes:
        return "Vault is already normalized."
    lines = [str(c) for c in changes]
    return "\n".join(lines)
