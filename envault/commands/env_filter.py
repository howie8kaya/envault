"""Filter vault secrets by prefix, suffix, or pattern."""
from __future__ import annotations
import fnmatch
from dataclasses import dataclass, field
from typing import Optional
from envault.vault import load_vault, save_vault, VaultError
from envault.crypto import decrypt, encrypt


class FilterError(Exception):
    pass


@dataclass
class FilterResult:
    matched: list[str] = field(default_factory=list)
    total: int = 0

    def __str__(self) -> str:
        return f"Matched {len(self.matched)}/{self.total} keys"


def filter_vault(
    vault_path: str,
    passphrase: str,
    *,
    prefix: Optional[str] = None,
    suffix: Optional[str] = None,
    pattern: Optional[str] = None,
    invert: bool = False,
) -> FilterResult:
    """Return keys matching the given filter criteria."""
    if not any([prefix, suffix, pattern]):
        raise FilterError("At least one of prefix, suffix, or pattern must be provided.")

    vault = load_vault(vault_path)
    secrets: dict = vault.get("secrets", {})
    total = len(secrets)
    matched = []

    for key in secrets:
        hit = False
        if prefix and key.startswith(prefix):
            hit = True
        if suffix and key.endswith(suffix):
            hit = True
        if pattern and fnmatch.fnmatch(key, pattern):
            hit = True
        if invert:
            hit = not hit
        if hit:
            matched.append(key)

    return FilterResult(matched=sorted(matched), total=total)


def extract_filtered(
    vault_path: str,
    passphrase: str,
    dest_path: str,
    dest_passphrase: str,
    **filter_kwargs,
) -> FilterResult:
    """Copy filtered keys from src vault into a new/existing dest vault."""
    result = filter_vault(vault_path, passphrase, **filter_kwargs)
    src_vault = load_vault(vault_path)
    try:
        dst_vault = load_vault(dest_path)
    except (FileNotFoundError, VaultError):
        dst_vault = {"secrets": {}}

    for key in result.matched:
        raw = src_vault["secrets"][key]
        value = decrypt(raw, passphrase)
        dst_vault["secrets"][key] = encrypt(value, dest_passphrase)

    save_vault(dest_path, dst_vault)
    return result
