"""env_patch.py — Apply a partial update (patch) to vault secrets from a dict or .env file."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from envault.vault import load_vault, save_vault, set_secret, VaultError
from envault.env_io import read_env_file, EnvParseError


class PatchError(Exception):
    pass


@dataclass
class PatchResult:
    applied: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    overwritten: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        lines = []
        if self.applied:
            lines.append(f"Added   ({len(self.applied)}): {', '.join(self.applied)}")
        if self.overwritten:
            lines.append(f"Updated ({len(self.overwritten)}): {', '.join(self.overwritten)}")
        if self.skipped:
            lines.append(f"Skipped ({len(self.skipped)}): {', '.join(self.skipped)}")
        return "\n".join(lines) if lines else "No changes."


def patch_vault(
    vault_path: Path,
    passphrase: str,
    updates: Dict[str, str],
    overwrite: bool = False,
    keys: Optional[List[str]] = None,
) -> PatchResult:
    """Apply *updates* dict to the vault, optionally restricted to *keys*."""
    try:
        data = load_vault(vault_path, passphrase)
    except VaultError as exc:
        raise PatchError(f"Failed to load vault: {exc}") from exc

    if keys is not None:
        unknown = [k for k in keys if k not in updates]
        if unknown:
            raise PatchError(f"Keys not present in patch source: {', '.join(unknown)}")
        updates = {k: updates[k] for k in keys}

    result = PatchResult()
    existing_keys = set(data.get("secrets", {}).keys())

    for key, value in updates.items():
        if key in existing_keys:
            if overwrite:
                set_secret(vault_path, passphrase, key, value)
                result.overwritten.append(key)
            else:
                result.skipped.append(key)
        else:
            set_secret(vault_path, passphrase, key, value)
            result.applied.append(key)

    return result


def patch_vault_from_file(
    vault_path: Path,
    passphrase: str,
    env_file: Path,
    overwrite: bool = False,
    keys: Optional[List[str]] = None,
) -> PatchResult:
    """Load a .env file and apply it as a patch to the vault."""
    try:
        updates = read_env_file(env_file)
    except (EnvParseError, OSError) as exc:
        raise PatchError(f"Failed to read env file: {exc}") from exc

    return patch_vault(vault_path, passphrase, updates, overwrite=overwrite, keys=keys)
