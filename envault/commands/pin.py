"""Pin secrets to specific versions, preventing accidental overwrites."""

from __future__ import annotations
from dataclasses import dataclass
from typing import List
from envault.vault import load_vault, save_vault, VaultError


class PinError(Exception):
    pass


@dataclass
class PinInfo:
    key: str
    pinned: bool

    def __str__(self) -> str:
        status = "pinned" if self.pinned else "unpinned"
        return f"{self.key}: {status}"


def _pin_meta(vault: dict) -> dict:
    return vault.setdefault("__meta__", {}).setdefault("pins", {})


def pin_secret(vault_path, passphrase: str, key: str) -> PinInfo:
    """Mark a secret as pinned so set_secret will refuse to overwrite it."""
    vault = load_vault(vault_path, passphrase)
    secrets = vault.get("secrets", {})
    if key not in secrets:
        raise PinError(f"Key not found: {key}")
    _pin_meta(vault)[key] = True
    save_vault(vault_path, passphrase, vault)
    return PinInfo(key=key, pinned=True)


def unpin_secret(vault_path, passphrase: str, key: str) -> PinInfo:
    """Remove pin from a secret."""
    vault = load_vault(vault_path, passphrase)
    meta = _pin_meta(vault)
    meta.pop(key, None)
    save_vault(vault_path, passphrase, vault)
    return PinInfo(key=key, pinned=False)


def is_pinned(vault_path, passphrase: str, key: str) -> bool:
    vault = load_vault(vault_path, passphrase)
    return _pin_meta(vault).get(key, False)


def list_pins(vault_path, passphrase: str) -> List[PinInfo]:
    vault = load_vault(vault_path, passphrase)
    secrets = vault.get("secrets", {})
    pins = _pin_meta(vault)
    return [PinInfo(key=k, pinned=pins.get(k, False)) for k in secrets]
