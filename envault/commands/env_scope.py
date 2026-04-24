"""Scope management: tag vault keys with a named scope and query by scope."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from envault.vault import VaultError, load_vault, save_vault


class ScopeError(Exception):
    pass


@dataclass
class ScopeInfo:
    key: str
    scope: str

    def __str__(self) -> str:
        return f"{self.key} -> scope:{self.scope}"


@dataclass
class ScopeResult:
    scope: str
    keys: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        joined = ", ".join(self.keys) if self.keys else "(none)"
        return f"scope:{self.scope} [{len(self.keys)} key(s)]: {joined}"


def _scope_meta(vault: dict) -> dict:
    return vault.setdefault("__meta__", {}).setdefault("scopes", {})


def set_scope(vault_path: str, passphrase: str, key: str, scope: str) -> ScopeInfo:
    """Assign *scope* to *key*.  Raises ScopeError if key is not in the vault."""
    if not scope or not scope.strip():
        raise ScopeError("scope name must not be empty")
    vault = load_vault(vault_path, passphrase)
    if key not in vault.get("secrets", {}):
        raise ScopeError(f"key not found: {key}")
    _scope_meta(vault)[key] = scope.strip()
    save_vault(vault_path, passphrase, vault)
    return ScopeInfo(key=key, scope=scope.strip())


def get_scope(vault_path: str, passphrase: str, key: str) -> Optional[str]:
    """Return the scope assigned to *key*, or None."""
    vault = load_vault(vault_path, passphrase)
    return _scope_meta(vault).get(key)


def remove_scope(vault_path: str, passphrase: str, key: str) -> bool:
    """Remove scope metadata for *key*.  Returns True if anything was removed."""
    vault = load_vault(vault_path, passphrase)
    meta = _scope_meta(vault)
    if key not in meta:
        return False
    del meta[key]
    save_vault(vault_path, passphrase, vault)
    return True


def list_by_scope(vault_path: str, passphrase: str, scope: str) -> ScopeResult:
    """Return all keys that belong to *scope*."""
    vault = load_vault(vault_path, passphrase)
    meta = _scope_meta(vault)
    keys = sorted(k for k, s in meta.items() if s == scope)
    return ScopeResult(scope=scope, keys=keys)


def all_scopes(vault_path: str, passphrase: str) -> dict:
    """Return a mapping of scope -> [keys] for every scoped key in the vault."""
    vault = load_vault(vault_path, passphrase)
    meta = _scope_meta(vault)
    result: dict = {}
    for key, scope in meta.items():
        result.setdefault(scope, []).append(key)
    return {s: sorted(ks) for s, ks in sorted(result.items())}
