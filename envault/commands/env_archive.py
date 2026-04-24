"""Archive (soft-delete) and restore secrets within a vault."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

from envault.vault import VaultError, load_vault, save_vault


class ArchiveError(Exception):
    pass


@dataclass
class ArchiveResult:
    key: str
    archived_at: Optional[str] = None
    restored: bool = False

    def __str__(self) -> str:
        if self.restored:
            return f"restored: {self.key}"
        return f"archived: {self.key} at {self.archived_at}"


def _archive_meta(vault: dict) -> dict:
    return vault.setdefault("__meta__", {}).setdefault("archived", {})


def archive_secret(vault_path: str, passphrase: str, key: str) -> ArchiveResult:
    """Soft-delete a secret by moving it to the archive namespace."""
    vault = load_vault(vault_path, passphrase)
    secrets: dict = vault.get("secrets", {})

    if key not in secrets:
        raise ArchiveError(f"Key '{key}' not found in vault")

    meta = _archive_meta(vault)
    archived_at = datetime.now(timezone.utc).isoformat()

    meta[key] = {
        "value": secrets.pop(key),
        "archived_at": archived_at,
    }

    save_vault(vault_path, passphrase, vault)
    return ArchiveResult(key=key, archived_at=archived_at)


def restore_secret(vault_path: str, passphrase: str, key: str) -> ArchiveResult:
    """Restore a previously archived secret back into active secrets."""
    vault = load_vault(vault_path, passphrase)
    meta = _archive_meta(vault)

    if key not in meta:
        raise ArchiveError(f"Key '{key}' is not archived")

    secrets: dict = vault.setdefault("secrets", {})
    if key in secrets:
        raise ArchiveError(f"Key '{key}' already exists in active secrets")

    secrets[key] = meta.pop(key)["value"]
    save_vault(vault_path, passphrase, vault)
    return ArchiveResult(key=key, restored=True)


def list_archived(vault_path: str, passphrase: str) -> List[ArchiveResult]:
    """Return all currently archived keys with their archive timestamps."""
    vault = load_vault(vault_path, passphrase)
    meta = _archive_meta(vault)
    return [
        ArchiveResult(key=k, archived_at=v["archived_at"])
        for k, v in meta.items()
    ]


def purge_archived(vault_path: str, passphrase: str) -> List[str]:
    """Permanently remove all archived secrets."""
    vault = load_vault(vault_path, passphrase)
    meta = _archive_meta(vault)
    removed = list(meta.keys())
    meta.clear()
    save_vault(vault_path, passphrase, vault)
    return removed
