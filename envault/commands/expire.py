"""Secret expiry/TTL tracking for vault entries."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

from envault.vault import VaultError, load_vault, save_vault

META_KEY = "__expire_meta__"


class ExpireError(Exception):
    pass


@dataclass
class ExpiryInfo:
    key: str
    expires_at: datetime
    expired: bool

    def __str__(self) -> str:
        status = "EXPIRED" if self.expired else "ok"
        return f"{self.key}: expires {self.expires_at.isoformat()} [{status}]"


def _meta(vault: dict) -> dict:
    return vault.get("meta", {}).get(META_KEY, {})


def set_expiry(vault_path: str, passphrase: str, key: str, days: int) -> datetime:
    """Set a TTL in days for a secret key."""
    vault = load_vault(vault_path)
    secrets = vault.get("secrets", {})
    if key not in secrets:
        raise ExpireError(f"Key '{key}' not found in vault.")
    if days <= 0:
        raise ExpireError("days must be a positive integer.")

    expires_at = datetime.now(timezone.utc) + timedelta(days=days)
    vault.setdefault("meta", {}).setdefault(META_KEY, {})
    vault["meta"][META_KEY][key] = expires_at.isoformat()
    save_vault(vault_path, vault)
    return expires_at


def get_expiry(vault_path: str, key: str) -> Optional[ExpiryInfo]:
    """Return expiry info for a key, or None if no expiry set."""
    vault = load_vault(vault_path)
    meta = _meta(vault)
    if key not in meta:
        return None
    expires_at = datetime.fromisoformat(meta[key])
    return ExpiryInfo(key=key, expires_at=expires_at, expired=datetime.now(timezone.utc) > expires_at)


def list_expiring(vault_path: str, within_days: int = 30) -> list[ExpiryInfo]:
    """List secrets expiring within the given number of days."""
    vault = load_vault(vault_path)
    meta = _meta(vault)
    now = datetime.now(timezone.utc)
    cutoff = now + timedelta(days=within_days)
    results = []
    for key, iso in meta.items():
        expires_at = datetime.fromisoformat(iso)
        if expires_at <= cutoff:
            results.append(ExpiryInfo(key=key, expires_at=expires_at, expired=now > expires_at))
    results.sort(key=lambda e: e.expires_at)
    return results


def clear_expiry(vault_path: str, key: str) -> bool:
    """Remove expiry for a key. Returns True if removed, False if not set."""
    vault = load_vault(vault_path)
    meta = vault.get("meta", {}).get(META_KEY, {})
    if key not in meta:
        return False
    del vault["meta"][META_KEY][key]
    save_vault(vault_path, vault)
    return True
