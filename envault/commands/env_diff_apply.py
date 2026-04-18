"""Apply a diff (from diff_vault_vs_file) back into the vault or a file."""
from __future__ import annotations
from pathlib import Path
from typing import List, Optional

from envault.vault import load_vault, save_vault, set_secret, VaultError
from envault.commands.diff import diff_vault_vs_file, DiffEntry
from envault.env_io import read_env_file, write_env_file


class ApplyError(Exception):
    pass


def apply_diff_to_vault(
    vault_path: Path,
    env_path: Path,
    passphrase: str,
    keys: Optional[List[str]] = None,
    overwrite: bool = False,
) -> List[DiffEntry]:
    """Import changed/added keys from an env file into the vault.

    Returns the list of DiffEntry items that were applied.
    """
    entries = diff_vault_vs_file(vault_path, env_path, passphrase)
    applied: List[DiffEntry] = []

    for entry in entries:
        if keys and entry.key not in keys:
            continue
        if entry.status == "same":
            continue
        if entry.status == "vault_only":
            continue
        if entry.status == "changed" and not overwrite:
            continue
        if entry.file_value is None:
            continue
        set_secret(vault_path, passphrase, entry.key, entry.file_value)
        applied.append(entry)

    return applied


def apply_diff_to_file(
    vault_path: Path,
    env_path: Path,
    passphrase: str,
    keys: Optional[List[str]] = None,
    overwrite: bool = False,
) -> List[DiffEntry]:
    """Export changed/added keys from the vault into an env file.

    Returns the list of DiffEntry items that were applied.
    """
    entries = diff_vault_vs_file(vault_path, env_path, passphrase)
    applied: List[DiffEntry] = []

    try:
        current = read_env_file(env_path)
    except FileNotFoundError:
        current = {}

    for entry in entries:
        if keys and entry.key not in keys:
            continue
        if entry.status == "same":
            continue
        if entry.status == "file_only":
            continue
        if entry.status == "changed" and not overwrite:
            continue
        if entry.vault_value is None:
            continue
        current[entry.key] = entry.vault_value
        applied.append(entry)

    if applied:
        write_env_file(env_path, current)

    return applied
