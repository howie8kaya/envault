"""Environment switching: save and restore named environment profiles."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from envault.vault import load_vault, save_vault, VaultError


class SwitchError(Exception):
    pass


def _profiles_path(vault_path: Path) -> Path:
    return vault_path.parent / (vault_path.stem + ".profiles.json")


def save_profile(vault_path: Path, passphrase: str, profile_name: str) -> None:
    """Snapshot the current vault state under a named profile."""
    vault = load_vault(vault_path, passphrase)
    profiles_path = _profiles_path(vault_path)

    if profiles_path.exists():
        profiles = json.loads(profiles_path.read_text())
    else:
        profiles = {}

    profiles[profile_name] = vault["secrets"]
    profiles_path.write_text(json.dumps(profiles, indent=2))


def switch_profile(vault_path: Path, passphrase: str, profile_name: str) -> int:
    """Switch the vault to a named profile. Returns number of keys restored."""
    profiles_path = _profiles_path(vault_path)

    if not profiles_path.exists():
        raise SwitchError("No profiles file found. Save a profile first.")

    profiles = json.loads(profiles_path.read_text())

    if profile_name not in profiles:
        raise SwitchError(f"Profile '{profile_name}' does not exist.")

    vault = load_vault(vault_path, passphrase)
    vault["secrets"] = profiles[profile_name]
    save_vault(vault_path, vault, passphrase)
    return len(profiles[profile_name])


def list_profiles(vault_path: Path) -> list[str]:
    """Return sorted list of saved profile names."""
    profiles_path = _profiles_path(vault_path)
    if not profiles_path.exists():
        return []
    profiles = json.loads(profiles_path.read_text())
    return sorted(profiles.keys())


def delete_profile(vault_path: Path, profile_name: str) -> bool:
    """Delete a named profile. Returns True if it existed."""
    profiles_path = _profiles_path(vault_path)
    if not profiles_path.exists():
        return False
    profiles = json.loads(profiles_path.read_text())
    if profile_name not in profiles:
        return False
    del profiles[profile_name]
    profiles_path.write_text(json.dumps(profiles, indent=2))
    return True
