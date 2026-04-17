"""Combine webhook firing with audit log recording."""
from __future__ import annotations
from pathlib import Path
from typing import List
from envault.commands.webhook import notify
from envault.commands.audit import record_event


def emit(vault_path: Path, passphrase: str, event: str, payload: dict) -> List[dict]:
    """Record an audit event and fire matching webhooks.

    Returns the list of webhook delivery results (may be empty if no hooks registered).
    """
    record_event(vault_path, event, payload)
    return notify(vault_path, passphrase, event, payload)


def emit_set(vault_path: Path, passphrase: str, key: str) -> List[dict]:
    return emit(vault_path, passphrase, "set", {"key": key})


def emit_delete(vault_path: Path, passphrase: str, key: str) -> List[dict]:
    return emit(vault_path, passphrase, "delete", {"key": key})


def emit_rotate(vault_path: Path, passphrase: str) -> List[dict]:
    return emit(vault_path, passphrase, "rotate", {})


def emit_import(vault_path: Path, passphrase: str, count: int) -> List[dict]:
    return emit(vault_path, passphrase, "import", {"count": count})


def emit_export(vault_path: Path, passphrase: str, count: int) -> List[dict]:
    return emit(vault_path, passphrase, "export", {"count": count})
