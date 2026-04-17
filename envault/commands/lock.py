"""Lock/unlock vault access with a session token to avoid repeated passphrase entry."""

from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path

LOCK_TTL_SECONDS = 3600  # 1 hour


class LockError(Exception):
    pass


def _session_path(vault_path: Path) -> Path:
    digest = hashlib.sha1(str(vault_path.resolve()).encode()).hexdigest()[:12]
    return Path(os.environ.get("TMPDIR", "/tmp")) / f".envault_session_{digest}"


def lock_vault(vault_path: Path) -> None:
    """Remove the session token, effectively locking the vault."""
    sp = _session_path(vault_path)
    if sp.exists():
        sp.unlink()


def unlock_vault(vault_path: Path, passphrase: str, ttl: int = LOCK_TTL_SECONDS) -> str:
    """Store a session token derived from the passphrase. Returns the token."""
    from envault.vault import load_vault  # verify passphrase is correct

    load_vault(vault_path, passphrase)  # raises VaultError on bad passphrase
    token = hashlib.sha256(f"{passphrase}:{time.time()}".encode()).hexdigest()
    sp = _session_path(vault_path)
    sp.write_text(
        json.dumps({"token": token, "passphrase": passphrase, "expires": time.time() + ttl})
    )
    sp.chmod(0o600)
    return token


def get_session_passphrase(vault_path: Path) -> str | None:
    """Return the cached passphrase if session is still valid, else None."""
    sp = _session_path(vault_path)
    if not sp.exists():
        return None
    try:
        data = json.loads(sp.read_text())
        if time.time() > data["expires"]:
            sp.unlink()
            return None
        return data["passphrase"]
    except (json.JSONDecodeError, KeyError):
        return None


def is_unlocked(vault_path: Path) -> bool:
    return get_session_passphrase(vault_path) is not None


def session_info(vault_path: Path) -> dict | None:
    """Return session metadata or None if locked."""
    sp = _session_path(vault_path)
    if not sp.exists():
        return None
    try:
        data = json.loads(sp.read_text())
        remaining = max(0, int(data["expires"] - time.time()))
        return {"expires_in": remaining, "token_prefix": data["token"][:8]}
    except (json.JSONDecodeError, KeyError):
        return None
