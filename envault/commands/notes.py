"""Attach and retrieve plaintext notes on vault secrets."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from envault.vault import load_vault, save_vault, VaultError


class NoteError(Exception):
    pass


@dataclass
class NoteInfo:
    key: str
    note: str

    def __str__(self) -> str:
        return f"{self.key}: {self.note}"


def _notes_meta(vault: dict) -> dict:
    return vault.setdefault("__meta__", {}).setdefault("notes", {})


def set_note(vault_path: str, passphrase: str, key: str, note: str) -> NoteInfo:
    """Attach a note to a secret key."""
    vault = load_vault(vault_path, passphrase)
    if key not in vault.get("secrets", {}):
        raise NoteError(f"Key not found: {key}")
    if not note.strip():
        raise NoteError("Note must not be empty.")
    _notes_meta(vault)[key] = note
    save_vault(vault_path, passphrase, vault)
    return NoteInfo(key=key, note=note)


def get_note(vault_path: str, passphrase: str, key: str) -> Optional[NoteInfo]:
    """Retrieve the note for a key, or None if not set."""
    vault = load_vault(vault_path, passphrase)
    note = _notes_meta(vault).get(key)
    if note is None:
        return None
    return NoteInfo(key=key, note=note)


def delete_note(vault_path: str, passphrase: str, key: str) -> bool:
    """Remove a note from a key. Returns True if deleted, False if none existed."""
    vault = load_vault(vault_path, passphrase)
    meta = _notes_meta(vault)
    if key not in meta:
        return False
    del meta[key]
    save_vault(vault_path, passphrase, vault)
    return True


def list_notes(vault_path: str, passphrase: str) -> list[NoteInfo]:
    """Return all notes across all keys."""
    vault = load_vault(vault_path, passphrase)
    meta = _notes_meta(vault)
    return [NoteInfo(key=k, note=v) for k, v in meta.items()]
