"""Add or strip a prefix from vault secret keys."""
from dataclasses import dataclass, field
from typing import List
from envault.vault import load_vault, save_vault, set_secret, get_secret, delete_secret, VaultError


class PrefixError(Exception):
    pass


@dataclass
class PrefixResult:
    affected: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        lines = [f"Affected: {len(self.affected)}, Skipped: {len(self.skipped)}"]
        for k in self.affected:
            lines.append(f"  ~ {k}")
        return "\n".join(lines)


def add_prefix(vault_path: str, passphrase: str, prefix: str, keys: List[str] = None, overwrite: bool = False) -> PrefixResult:
    """Add a prefix to the specified keys (or all keys)."""
    if not prefix:
        raise PrefixError("Prefix must not be empty.")
    vault = load_vault(vault_path)
    all_keys = list(vault["secrets"].keys())
    targets = keys if keys is not None else all_keys
    result = PrefixResult()
    for key in targets:
        if key not in vault["secrets"]:
            raise PrefixError(f"Key not found: {key}")
        new_key = f"{prefix}{key}"
        if new_key in vault["secrets"] and not overwrite:
            result.skipped.append(key)
            continue
        value = get_secret(vault_path, passphrase, key)
        set_secret(vault_path, passphrase, new_key, value)
        delete_secret(vault_path, key)
        result.affected.append(new_key)
    return result


def strip_prefix(vault_path: str, passphrase: str, prefix: str, keys: List[str] = None, overwrite: bool = False) -> PrefixResult:
    """Strip a prefix from the specified keys (or all matching keys)."""
    if not prefix:
        raise PrefixError("Prefix must not be empty.")
    vault = load_vault(vault_path)
    all_keys = list(vault["secrets"].keys())
    targets = keys if keys is not None else [k for k in all_keys if k.startswith(prefix)]
    result = PrefixResult()
    for key in targets:
        if key not in vault["secrets"]:
            raise PrefixError(f"Key not found: {key}")
        if not key.startswith(prefix):
            result.skipped.append(key)
            continue
        new_key = key[len(prefix):]
        if not new_key:
            result.skipped.append(key)
            continue
        if new_key in vault["secrets"] and not overwrite:
            result.skipped.append(key)
            continue
        value = get_secret(vault_path, passphrase, key)
        set_secret(vault_path, passphrase, new_key, value)
        delete_secret(vault_path, key)
        result.affected.append(new_key)
    return result


def list_prefix_candidates(vault_path: str, prefix: str) -> List[str]:
    """List keys that start with the given prefix."""
    vault = load_vault(vault_path)
    return [k for k in vault["secrets"] if k.startswith(prefix)]
