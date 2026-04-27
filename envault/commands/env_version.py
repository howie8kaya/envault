"""Version tracking for individual secrets in a vault."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import List, Optional

from envault.vault import VaultError, load_vault, save_vault


class VersionError(Exception):
    pass


@dataclass
class VersionEntry:
    version: int
    value: str
    recorded_at: float
    note: Optional[str] = None

    def __str__(self) -> str:
        ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.recorded_at))
        note_part = f" ({self.note})" if self.note else ""
        preview = self.value[:8] + "..." if len(self.value) > 8 else self.value
        return f"v{self.version} [{ts}]{note_part}: {preview!r}"


def _version_meta(vault: dict) -> dict:
    return vault.setdefault("__meta__", {}).setdefault("versions", {})


def record_version(
    vault_path: str,
    passphrase: str,
    key: str,
    note: Optional[str] = None,
) -> VersionEntry:
    """Snapshot the current value of a key into its version history."""
    from envault.crypto import decrypt

    vault = load_vault(vault_path, passphrase)
    secrets = vault.get("secrets", {})
    if key not in secrets:
        raise VersionError(f"Key {key!r} not found in vault")

    raw = decrypt(secrets[key], passphrase)
    meta = _version_meta(vault)
    history: List[dict] = meta.get(key, [])
    version_num = len(history) + 1
    entry_dict = {
        "version": version_num,
        "value": raw,
        "recorded_at": time.time(),
        "note": note,
    }
    history.append(entry_dict)
    meta[key] = history
    save_vault(vault_path, passphrase, vault)
    return VersionEntry(**entry_dict)


def get_versions(vault_path: str, passphrase: str, key: str) -> List[VersionEntry]:
    """Return all recorded versions for a key."""
    vault = load_vault(vault_path, passphrase)
    meta = _version_meta(vault)
    return [VersionEntry(**e) for e in meta.get(key, [])]


def rollback(
    vault_path: str,
    passphrase: str,
    key: str,
    version: int,
) -> VersionEntry:
    """Restore a key's value to a previously recorded version."""
    from envault.crypto import encrypt

    vault = load_vault(vault_path, passphrase)
    meta = _version_meta(vault)
    history = meta.get(key, [])
    if not history:
        raise VersionError(f"No version history for key {key!r}")
    matches = [e for e in history if e["version"] == version]
    if not matches:
        raise VersionError(f"Version {version} not found for key {key!r}")
    target = matches[0]
    vault.setdefault("secrets", {})[key] = encrypt(target["value"], passphrase)
    save_vault(vault_path, passphrase, vault)
    return VersionEntry(**target)
