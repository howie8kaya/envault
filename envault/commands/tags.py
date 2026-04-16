"""Tag secrets in a vault for grouping and filtering."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict
from envault.vault import load_vault, save_vault, VaultError


class TagError(Exception):
    pass


@dataclass
class TagSummary:
    key: str
    tags: List[str]

    def __str__(self) -> str:
        return f"{self.key}: {', '.join(self.tags) if self.tags else '(none)'}"


def _tags_meta(vault: dict) -> Dict[str, List[str]]:
    return vault.setdefault("_meta", {}).setdefault("tags", {})


def add_tag(vault_path: str, passphrase: str, key: str, tag: str) -> List[str]:
    vault = load_vault(vault_path, passphrase)
    secrets = vault.get("secrets", {})
    if key not in secrets:
        raise TagError(f"Key '{key}' not found in vault.")
    tags = _tags_meta(vault)
    key_tags = tags.setdefault(key, [])
    if tag not in key_tags:
        key_tags.append(tag)
    save_vault(vault_path, passphrase, vault)
    return key_tags


def remove_tag(vault_path: str, passphrase: str, key: str, tag: str) -> List[str]:
    vault = load_vault(vault_path, passphrase)
    tags = _tags_meta(vault)
    key_tags = tags.get(key, [])
    if tag not in key_tags:
        raise TagError(f"Tag '{tag}' not present on key '{key}'.")
    key_tags.remove(tag)
    tags[key] = key_tags
    save_vault(vault_path, passphrase, vault)
    return key_tags


def list_tags(vault_path: str, passphrase: str) -> List[TagSummary]:
    vault = load_vault(vault_path, passphrase)
    secrets = vault.get("secrets", {})
    tags = _tags_meta(vault)
    return [TagSummary(key=k, tags=tags.get(k, [])) for k in secrets]


def filter_by_tag(vault_path: str, passphrase: str, tag: str) -> List[str]:
    vault = load_vault(vault_path, passphrase)
    tags = _tags_meta(vault)
    return [k for k, t in tags.items() if tag in t]
