"""Redact secrets from a text blob using vault keys."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from envault.vault import load_vault, decrypt
from envault.crypto import decrypt as crypto_decrypt


class RedactError(Exception):
    pass


@dataclass
class RedactResult:
    original: str
    redacted: str
    replaced: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        count = len(self.replaced)
        keys = ", ".join(self.replaced) if self.replaced else "none"
        return f"Redacted {count} secret(s): {keys}"


def redact_text(
    text: str,
    vault_path: str,
    passphrase: str,
    placeholder: str = "[REDACTED]",
    min_length: int = 4,
) -> RedactResult:
    """Replace occurrences of vault secret values in *text* with *placeholder*."""
    vault = load_vault(vault_path)
    replaced: list[str] = []
    result = text

    for key, ciphertext in vault.get("secrets", {}).items():
        try:
            value = crypto_decrypt(ciphertext, passphrase)
        except Exception:
            continue
        if len(value) < min_length:
            continue
        if value in result:
            result = result.replace(value, placeholder)
            replaced.append(key)

    return RedactResult(original=text, redacted=result, replaced=replaced)


def redact_file(
    file_path: str,
    vault_path: str,
    passphrase: str,
    placeholder: str = "[REDACTED]",
    min_length: int = 4,
    write: bool = False,
) -> RedactResult:
    """Redact secrets from a file, optionally writing the result back."""
    try:
        with open(file_path, "r", encoding="utf-8") as fh:
            text = fh.read()
    except OSError as exc:
        raise RedactError(f"Cannot read file: {exc}") from exc

    result = redact_text(text, vault_path, passphrase, placeholder, min_length)

    if write:
        try:
            with open(file_path, "w", encoding="utf-8") as fh:
                fh.write(result.redacted)
        except OSError as exc:
            raise RedactError(f"Cannot write file: {exc}") from exc

    return result
