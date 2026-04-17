"""Alias management: create short aliases for vault secret keys."""

from __future__ import annotations
from dataclasses import dataclass
from envault.vault import load_vault, save_vault, VaultError


class AliasError(Exception):
    pass


@dataclass
class AliasInfo:
    alias: str
    key: str

    def __str__(self) -> str:
        return f"{self.alias} -> {self.key}"


def _alias_meta(vault: dict) -> dict:
    return vault.setdefault("__meta__", {}).setdefault("aliases", {})


def set_alias(vault_path, alias: str, key: str, passphrase: str) -> AliasInfo:
    """Create or overwrite an alias pointing to a vault key."""
    vault = load_vault(vault_path, passphrase)
    if key not in vault["secrets"]:
        raise AliasError(f"Key '{key}' not found in vault.")
    if not alias or not alias.isidentifier():
        raise AliasError(f"Alias '{alias}' is not a valid identifier.")
    _alias_meta(vault)[alias] = key
    save_vault(vault_path, vault, passphrase)
    return AliasInfo(alias=alias, key=key)


def remove_alias(vault_path, alias: str, passphrase: str) -> None:
    """Remove an alias."""
    vault = load_vault(vault_path, passphrase)
    meta = _alias_meta(vault)
    if alias not in meta:
        raise AliasError(f"Alias '{alias}' does not exist.")
    del meta[alias]
    save_vault(vault_path, vault, passphrase)


def resolve_alias(vault_path, alias: str, passphrase: str) -> AliasInfo:
    """Resolve an alias to its target key."""
    vault = load_vault(vault_path, passphrase)
    meta = _alias_meta(vault)
    if alias not in meta:
        raise AliasError(f"Alias '{alias}' does not exist.")
    return AliasInfo(alias=alias, key=meta[alias])


def list_aliases(vault_path, passphrase: str) -> list[AliasInfo]:
    """Return all defined aliases."""
    vault = load_vault(vault_path, passphrase)
    meta = _alias_meta(vault)
    return [AliasInfo(alias=a, key=k) for a, k in meta.items()]
