"""Dependency tracking between secrets."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from envault.vault import load_vault, save_vault, VaultError


class DepsError(Exception):
    pass


@dataclass
class DepInfo:
    key: str
    depends_on: list[str]

    def __str__(self) -> str:
        if self.depends_on:
            return f"{self.key} -> [{', '.join(self.depends_on)}]"
        return f"{self.key} -> (no dependencies)"


def _deps_meta(vault: dict) -> dict:
    return vault.setdefault("__meta__", {}).setdefault("deps", {})


def add_dependency(vault_path, key: str, depends_on: str, passphrase: str) -> DepInfo:
    vault = load_vault(vault_path, passphrase)
    secrets = vault.get("secrets", {})
    if key not in secrets:
        raise DepsError(f"Key not found: {key}")
    if depends_on not in secrets:
        raise DepsError(f"Dependency key not found: {depends_on}")
    meta = _deps_meta(vault)
    deps = meta.setdefault(key, [])
    if depends_on not in deps:
        deps.append(depends_on)
    save_vault(vault_path, vault, passphrase)
    return DepInfo(key=key, depends_on=deps)


def remove_dependency(vault_path, key: str, depends_on: str, passphrase: str) -> DepInfo:
    vault = load_vault(vault_path, passphrase)
    meta = _deps_meta(vault)
    deps = meta.get(key, [])
    if depends_on not in deps:
        raise DepsError(f"Dependency '{depends_on}' not found for key '{key}'")
    deps.remove(depends_on)
    meta[key] = deps
    save_vault(vault_path, vault, passphrase)
    return DepInfo(key=key, depends_on=deps)


def get_dependencies(vault_path, key: str, passphrase: str) -> DepInfo:
    vault = load_vault(vault_path, passphrase)
    if key not in vault.get("secrets", {}):
        raise DepsError(f"Key not found: {key}")
    meta = _deps_meta(vault)
    return DepInfo(key=key, depends_on=meta.get(key, []))


def get_dependents(vault_path, key: str, passphrase: str) -> list[str]:
    """Return all keys that depend on the given key."""
    vault = load_vault(vault_path, passphrase)
    if key not in vault.get("secrets", {}):
        raise DepsError(f"Key not found: {key}")
    meta = _deps_meta(vault)
    return [k for k, deps in meta.items() if key in deps]
