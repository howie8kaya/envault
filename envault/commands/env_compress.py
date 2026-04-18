"""Compress and decompress vault exports to reduce sharing payload size."""
from __future__ import annotations

import base64
import json
import zlib
from dataclasses import dataclass
from pathlib import Path

from envault.vault import load_vault, VaultError
from envault.crypto import decrypt, encrypt


class CompressError(Exception):
    pass


@dataclass
class CompressResult:
    key_count: int
    original_size: int
    compressed_size: int
    payload: str

    def __str__(self) -> str:
        ratio = 100 * (1 - self.compressed_size / max(self.original_size, 1))
        return (
            f"Compressed {self.key_count} keys: "
            f"{self.original_size}B -> {self.compressed_size}B "
            f"({ratio:.1f}% reduction)"
        )


def compress_vault(vault_path: Path, passphrase: str, keys: list[str] | None = None) -> CompressResult:
    """Export selected (or all) secrets as a compressed base64 payload."""
    data = load_vault(vault_path)
    secrets = data.get("secrets", {})

    if keys is not None:
        missing = [k for k in keys if k not in secrets]
        if missing:
            raise CompressError(f"Keys not found in vault: {missing}")
        secrets = {k: secrets[k] for k in keys}

    plaintext_map: dict[str, str] = {}
    for key, ciphertext in secrets.items():
        try:
            plaintext_map[key] = decrypt(ciphertext, passphrase)
        except Exception as exc:
            raise CompressError(f"Failed to decrypt '{key}': {exc}") from exc

    raw = json.dumps(plaintext_map, separators=(",", ":")).encode()
    compressed = zlib.compress(raw, level=9)
    payload = base64.b85encode(compressed).decode()

    return CompressResult(
        key_count=len(plaintext_map),
        original_size=len(raw),
        compressed_size=len(compressed),
        payload=payload,
    )


def decompress_into_vault(payload: str, passphrase: str, vault_path: Path, overwrite: bool = False) -> list[str]:
    """Decode a compressed payload and store secrets into vault, returning imported keys."""
    try:
        raw = zlib.decompress(base64.b85decode(payload.encode()))
        plaintext_map: dict[str, str] = json.loads(raw)
    except Exception as exc:
        raise CompressError(f"Invalid payload: {exc}") from exc

    try:
        data = load_vault(vault_path)
    except VaultError:
        data = {"secrets": {}}

    imported: list[str] = []
    for key, value in plaintext_map.items():
        if key in data["secrets"] and not overwrite:
            continue
        data["secrets"][key] = encrypt(value, passphrase)
        imported.append(key)

    from envault.vault import save_vault
    save_vault(vault_path, data)
    return imported
