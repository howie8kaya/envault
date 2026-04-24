"""Base64 encode/decode secrets stored in the vault."""

from __future__ import annotations

import base64
from dataclasses import dataclass, field
from typing import List, Optional

from envault.vault import VaultError, load_vault, save_vault, get_secret, set_secret


class EncodeError(Exception):
    pass


@dataclass
class EncodeResult:
    encoded: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        lines = []
        if self.encoded:
            lines.append(f"Encoded ({len(self.encoded)}): {', '.join(self.encoded)}")
        if self.skipped:
            lines.append(f"Skipped ({len(self.skipped)}): {', '.join(self.skipped)}")
        return "\n".join(lines) if lines else "Nothing to encode."


@dataclass
class DecodeResult:
    decoded: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        lines = []
        if self.decoded:
            lines.append(f"Decoded ({len(self.decoded)}): {', '.join(self.decoded)}")
        if self.skipped:
            lines.append(f"Skipped ({len(self.skipped)}): {', '.join(self.skipped)}")
        return "\n".join(lines) if lines else "Nothing to decode."


def encode_secrets(
    vault_path: str,
    passphrase: str,
    keys: Optional[List[str]] = None,
    overwrite: bool = True,
) -> EncodeResult:
    """Base64-encode the values of secrets in the vault."""
    vault = load_vault(vault_path, passphrase)
    all_keys = keys if keys is not None else list(vault.get("secrets", {}).keys())
    result = EncodeResult()

    for key in all_keys:
        try:
            raw = get_secret(vault_path, passphrase, key)
        except VaultError:
            raise EncodeError(f"Key not found: {key}")

        encoded_val = base64.b64encode(raw.encode()).decode()
        if encoded_val == raw and not overwrite:
            result.skipped.append(key)
            continue

        set_secret(vault_path, passphrase, key, encoded_val)
        result.encoded.append(key)

    return result


def decode_secrets(
    vault_path: str,
    passphrase: str,
    keys: Optional[List[str]] = None,
) -> DecodeResult:
    """Base64-decode the values of secrets in the vault."""
    vault = load_vault(vault_path, passphrase)
    all_keys = keys if keys is not None else list(vault.get("secrets", {}).keys())
    result = DecodeResult()

    for key in all_keys:
        try:
            raw = get_secret(vault_path, passphrase, key)
        except VaultError:
            raise EncodeError(f"Key not found: {key}")

        try:
            decoded_val = base64.b64decode(raw.encode()).decode()
        except Exception:
            result.skipped.append(key)
            continue

        set_secret(vault_path, passphrase, key, decoded_val)
        result.decoded.append(key)

    return result
