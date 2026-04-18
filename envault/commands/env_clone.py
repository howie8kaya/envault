"""Clone a vault to a new file, optionally filtering keys by prefix."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from envault.vault import VaultError, load_vault, init_vault, set_secret


class CloneError(Exception):
    pass


@dataclass
class CloneResult:
    source: Path
    destination: Path
    keys_copied: List[str] = field(default_factory=list)
    keys_skipped: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        return (
            f"Cloned {len(self.keys_copied)} key(s) from '{self.source}' "
            f"to '{self.destination}' "
            f"({len(self.keys_skipped)} skipped)."
        )


def clone_vault(
    src_path: Path,
    dst_path: Path,
    src_passphrase: str,
    dst_passphrase: str,
    prefix: Optional[str] = None,
    overwrite: bool = False,
) -> CloneResult:
    """Clone secrets from src vault into a new dst vault.

    Args:
        src_path: Path to the source vault.
        dst_path: Path for the destination vault.
        src_passphrase: Passphrase for the source vault.
        dst_passphrase: Passphrase for the destination vault.
        prefix: If given, only keys starting with this prefix are copied.
        overwrite: If True, overwrite dst_path if it already exists.
    """
    if not src_path.exists():
        raise CloneError(f"Source vault not found: {src_path}")

    src_vault = load_vault(src_path, src_passphrase)
    all_keys: List[str] = list(src_vault.get("secrets", {}).keys())

    init_vault(dst_path, dst_passphrase, overwrite=overwrite)

    result = CloneResult(source=src_path, destination=dst_path)

    for key in all_keys:
        if prefix and not key.startswith(prefix):
            result.keys_skipped.append(key)
            continue
        try:
            from envault.vault import get_secret
            value = get_secret(src_path, src_passphrase, key)
            set_secret(dst_path, dst_passphrase, key, value)
            result.keys_copied.append(key)
        except VaultError as exc:
            raise CloneError(f"Failed to clone key '{key}': {exc}") from exc

    return result


def list_clone_candidates(src_path: Path, src_passphrase: str, prefix: Optional[str] = None) -> List[str]:
    """Return keys that would be copied given a prefix filter."""
    vault = load_vault(src_path, src_passphrase)
    keys = list(vault.get("secrets", {}).keys())
    if prefix:
        keys = [k for k in keys if k.startswith(prefix)]
    return sorted(keys)
