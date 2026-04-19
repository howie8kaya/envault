"""Bulk uppercase all keys in a vault."""
from dataclasses import dataclass, field
from typing import List
from envault.vault import load_vault, save_vault, get_secret, set_secret, delete_secret, VaultError


class UppercaseError(Exception):
    pass


@dataclass
class UppercaseResult:
    renamed: List[tuple] = field(default_factory=list)  # (old, new)
    skipped: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        lines = []
        for old, new in self.renamed:
            lines.append(f"  {old} -> {new}")
        if self.skipped:
            lines.append(f"  skipped (already uppercase): {', '.join(self.skipped)}")
        return "\n".join(lines) if lines else "  nothing to change"


def uppercase_keys(vault_path: str, passphrase: str, keys: List[str] = None) -> UppercaseResult:
    """Uppercase all (or selected) keys in a vault."""
    data = load_vault(vault_path)
    secrets = data.get("secrets", {})

    targets = keys if keys is not None else list(secrets.keys())
    for k in targets:
        if k not in secrets:
            raise UppercaseError(f"Key not found: {k}")

    result = UppercaseResult()

    for old_key in targets:
        new_key = old_key.upper()
        if new_key == old_key:
            result.skipped.append(old_key)
            continue
        value = get_secret(vault_path, old_key, passphrase)
        if new_key in secrets and new_key != old_key:
            raise UppercaseError(f"Cannot rename '{old_key}' to '{new_key}': key already exists")
        set_secret(vault_path, new_key, value, passphrase)
        delete_secret(vault_path, old_key)
        result.renamed.append((old_key, new_key))

    return result


def list_uppercase_candidates(vault_path: str) -> List[str]:
    """Return keys that are not already fully uppercase."""
    data = load_vault(vault_path)
    return [k for k in data.get("secrets", {}) if k != k.upper()]
