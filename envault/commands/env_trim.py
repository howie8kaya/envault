"""Trim whitespace and normalize secrets in the vault."""

from dataclasses import dataclass, field
from typing import List
from envault.vault import load_vault, save_vault, get_secret, set_secret, list_secrets


class TrimError(Exception):
    pass


@dataclass
class TrimResult:
    changed: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        lines = []
        if self.changed:
            lines.append(f"Trimmed {len(self.changed)} key(s): {', '.join(self.changed)}")
        else:
            lines.append("No keys needed trimming.")
        if self.skipped:
            lines.append(f"Skipped {len(self.skipped)} key(s) (already clean).")
        return "\n".join(lines)


def trim_vault(vault_path: str, passphrase: str, keys: List[str] = None) -> TrimResult:
    """Strip leading/trailing whitespace from secret values in the vault."""
    data = load_vault(vault_path)
    all_keys = list_secrets(data)

    targets = keys if keys is not None else all_keys
    missing = [k for k in targets if k not in all_keys]
    if missing:
        raise TrimError(f"Keys not found in vault: {', '.join(missing)}")

    result = TrimResult()
    for key in targets:
        value = get_secret(data, key, passphrase)
        trimmed = value.strip()
        if trimmed != value:
            set_secret(data, key, trimmed, passphrase)
            result.changed.append(key)
        else:
            result.skipped.append(key)

    if result.changed:
        save_vault(vault_path, data)

    return result


def list_trim_candidates(vault_path: str, passphrase: str) -> List[str]:
    """Return keys whose values have leading or trailing whitespace."""
    data = load_vault(vault_path)
    candidates = []
    for key in list_secrets(data):
        value = get_secret(data, key, passphrase)
        if value != value.strip():
            candidates.append(key)
    return candidates
