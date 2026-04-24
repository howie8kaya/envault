"""Lightweight named checkpoints for vault state — lighter than full snapshots."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from envault.vault import load_vault, VaultError


class CheckpointError(Exception):
    pass


@dataclass
class CheckpointEntry:
    name: str
    created_at: float
    key_count: int
    keys: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.created_at))
        return f"[{self.name}] {ts} — {self.key_count} key(s): {', '.join(self.keys) or '(none)'}"


def _checkpoint_path(vault_path: Path) -> Path:
    return vault_path.parent / (vault_path.stem + ".checkpoints.json")


def _load_store(vault_path: Path) -> dict:
    cp = _checkpoint_path(vault_path)
    if not cp.exists():
        return {}
    try:
        return json.loads(cp.read_text())
    except (json.JSONDecodeError, OSError) as exc:
        raise CheckpointError(f"Failed to read checkpoint store: {exc}") from exc


def _save_store(vault_path: Path, store: dict) -> None:
    cp = _checkpoint_path(vault_path)
    cp.write_text(json.dumps(store, indent=2))


def create_checkpoint(vault_path: Path, passphrase: str, name: str) -> CheckpointEntry:
    """Record a named checkpoint of the current vault key list."""
    if not name or not name.strip():
        raise CheckpointError("Checkpoint name must not be empty.")
    vault = load_vault(vault_path, passphrase)
    keys = sorted(vault.get("secrets", {}).keys())
    store = _load_store(vault_path)
    entry = {
        "created_at": time.time(),
        "key_count": len(keys),
        "keys": keys,
    }
    store[name] = entry
    _save_store(vault_path, store)
    return CheckpointEntry(name=name, **entry)


def get_checkpoint(vault_path: Path, name: str) -> Optional[CheckpointEntry]:
    """Retrieve a checkpoint by name, or None if it does not exist."""
    store = _load_store(vault_path)
    raw = store.get(name)
    if raw is None:
        return None
    return CheckpointEntry(name=name, **raw)


def list_checkpoints(vault_path: Path) -> List[CheckpointEntry]:
    """Return all checkpoints sorted by creation time."""
    store = _load_store(vault_path)
    entries = [CheckpointEntry(name=n, **v) for n, v in store.items()]
    return sorted(entries, key=lambda e: e.created_at)


def delete_checkpoint(vault_path: Path, name: str) -> bool:
    """Remove a checkpoint by name. Returns True if it existed."""
    store = _load_store(vault_path)
    if name not in store:
        return False
    del store[name]
    _save_store(vault_path, store)
    return True
