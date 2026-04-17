"""TTL (time-to-live) support for vault secrets."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
import json
from envault.vault import load_vault, save_vault, VaultError


class TTLError(Exception):
    pass


@dataclass
class TTLInfo:
    key: str
    expires_at: datetime
    remaining_seconds: float

    def __str__(self) -> str:
        secs = max(0, int(self.remaining_seconds))
        return f"{self.key}: expires at {self.expires_at.isoformat()} ({secs}s remaining)"

    @property
    def is_expired(self) -> bool:
        return self.remaining_seconds <= 0


def _ttl_meta(vault_path: Path) -> Path:
    return vault_path.with_suffix(".ttl.json")


def set_ttl(vault_path: Path, passphrase: str, key: str, seconds: int) -> TTLInfo:
    if seconds <= 0:
        raise TTLError("TTL must be a positive number of seconds")
    vault = load_vault(vault_path, passphrase)
    if key not in vault:
        raise TTLError(f"Key not found: {key}")
    meta_path = _ttl_meta(vault_path)
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=seconds)
    meta[key] = expires_at.isoformat()
    meta_path.write_text(json.dumps(meta, indent=2))
    remaining = (expires_at - datetime.now(timezone.utc)).total_seconds()
    return TTLInfo(key=key, expires_at=expires_at, remaining_seconds=remaining)


def get_ttl(vault_path: Path, key: str) -> TTLInfo | None:
    meta_path = _ttl_meta(vault_path)
    if not meta_path.exists():
        return None
    meta = json.loads(meta_path.read_text())
    if key not in meta:
        return None
    expires_at = datetime.fromisoformat(meta[key])
    remaining = (expires_at - datetime.now(timezone.utc)).total_seconds()
    return TTLInfo(key=key, expires_at=expires_at, remaining_seconds=remaining)


def purge_expired(vault_path: Path, passphrase: str) -> list[str]:
    """Remove all secrets whose TTL has elapsed. Returns list of purged keys."""
    meta_path = _ttl_meta(vault_path)
    if not meta_path.exists():
        return []
    meta = json.loads(meta_path.read_text())
    now = datetime.now(timezone.utc)
    expired = [k for k, ts in meta.items() if datetime.fromisoformat(ts) <= now]
    if not expired:
        return []
    vault = load_vault(vault_path, passphrase)
    for k in expired:
        vault.pop(k, None)
        del meta[k]
    save_vault(vault_path, passphrase, vault)
    meta_path.write_text(json.dumps(meta, indent=2))
    return expired
