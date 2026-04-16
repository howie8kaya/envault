"""Track per-key value history inside the vault metadata."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

from envault.vault import VaultError, load_vault, save_vault


HISTORY_META_KEY = "__history__"


class HistoryError(Exception):
    pass


@dataclass
class HistoryEntry:
    timestamp: str
    value_preview: str  # first 6 chars + "..."

    def __str__(self) -> str:
        return f"[{self.timestamp}] {self.value_preview}"


def _preview(value: str) -> str:
    return value[:6] + "..." if len(value) > 6 else value


def record_history(vault_path: str, key: str, value: str, passphrase: str) -> None:
    """Append a history entry for key after a set operation."""
    vault = load_vault(vault_path, passphrase)
    meta = vault.get("meta", {})
    history: dict = meta.get(HISTORY_META_KEY, {})
    entries: list = history.get(key, [])
    entries.append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "value_preview": _preview(value),
    })
    history[key] = entries
    meta[HISTORY_META_KEY] = history
    vault["meta"] = meta
    save_vault(vault_path, vault, passphrase)


def get_history(vault_path: str, key: str, passphrase: str) -> List[HistoryEntry]:
    """Return recorded history entries for a key."""
    vault = load_vault(vault_path, passphrase)
    history = vault.get("meta", {}).get(HISTORY_META_KEY, {})
    raw = history.get(key, [])
    return [HistoryEntry(e["timestamp"], e["value_preview"]) for e in raw]


def clear_history(vault_path: str, key: str, passphrase: str) -> int:
    """Clear history for a key. Returns number of entries removed."""
    vault = load_vault(vault_path, passphrase)
    meta = vault.get("meta", {})
    history = meta.get(HISTORY_META_KEY, {})
    count = len(history.get(key, []))
    history.pop(key, None)
    meta[HISTORY_META_KEY] = history
    vault["meta"] = meta
    save_vault(vault_path, vault, passphrase)
    return count


def list_tracked_keys(vault_path: str, passphrase: str) -> List[str]:
    """Return all keys that have at least one history entry."""
    vault = load_vault(vault_path, passphrase)
    history = vault.get("meta", {}).get(HISTORY_META_KEY, {})
    return [k for k, v in history.items() if v]
