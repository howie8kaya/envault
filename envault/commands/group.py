"""Group secrets under named logical groups for organization."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from envault.vault import load_vault, save_vault, VaultError


class GroupError(Exception):
    pass


@dataclass
class GroupInfo:
    name: str
    keys: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        return f"[{self.name}] {', '.join(self.keys) if self.keys else '(empty)'}"


def _groups_meta(vault: dict) -> dict:
    return vault.setdefault("__meta__", {}).setdefault("groups", {})


def add_to_group(vault_path, passphrase: str, group: str, key: str) -> GroupInfo:
    vault = load_vault(vault_path, passphrase)
    if key not in vault.get("secrets", {}):
        raise GroupError(f"Key '{key}' not found in vault")
    groups = _groups_meta(vault)
    members = groups.setdefault(group, [])
    if key not in members:
        members.append(key)
    save_vault(vault_path, vault, passphrase)
    return GroupInfo(name=group, keys=list(members))


def remove_from_group(vault_path, passphrase: str, group: str, key: str) -> GroupInfo:
    vault = load_vault(vault_path, passphrase)
    groups = _groups_meta(vault)
    if group not in groups:
        raise GroupError(f"Group '{group}' does not exist")
    members = groups[group]
    if key not in members:
        raise GroupError(f"Key '{key}' is not in group '{group}'")
    members.remove(key)
    save_vault(vault_path, vault, passphrase)
    return GroupInfo(name=group, keys=list(members))


def list_groups(vault_path, passphrase: str) -> List[GroupInfo]:
    vault = load_vault(vault_path, passphrase)
    groups = _groups_meta(vault)
    return [GroupInfo(name=name, keys=list(keys)) for name, keys in groups.items()]


def get_group(vault_path, passphrase: str, group: str) -> Optional[GroupInfo]:
    vault = load_vault(vault_path, passphrase)
    groups = _groups_meta(vault)
    if group not in groups:
        return None
    return GroupInfo(name=group, keys=list(groups[group]))


def delete_group(vault_path, passphrase: str, group: str) -> bool:
    vault = load_vault(vault_path, passphrase)
    groups = _groups_meta(vault)
    if group not in groups:
        raise GroupError(f"Group '{group}' does not exist")
    del groups[group]
    save_vault(vault_path, vault, passphrase)
    return True
