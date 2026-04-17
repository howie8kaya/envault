"""Mask/redact secret values for safe display or logging."""

from __future__ import annotations
from dataclasses import dataclass
from envault.vault import load_vault, VaultError


class MaskError(Exception):
    pass


@dataclass
class MaskedEntry:
    key: str
    masked: str
    length: int

    def __str__(self) -> str:
        return f"{self.key}={self.masked} ({self.length} chars)"


def _mask_value(value: str, reveal: int = 0) -> str:
    """Return masked version of value, optionally revealing first N chars."""
    if not value:
        return ""
    if reveal and reveal < len(value):
        return value[:reveal] + "*" * (len(value) - reveal)
    return "*" * len(value)


def mask_secrets(
    vault_path: str,
    passphrase: str,
    keys: list[str] | None = None,
    reveal: int = 0,
) -> list[MaskedEntry]:
    """Load vault and return masked representations of secrets.

    Args:
        vault_path: Path to the vault file.
        passphrase: Vault passphrase.
        keys: Optional list of keys to mask; if None, masks all.
        reveal: Number of leading characters to reveal (0 = fully masked).

    Returns:
        List of MaskedEntry objects.
    """
    vault = load_vault(vault_path, passphrase)
    secrets = vault.get("secrets", {})

    target_keys = keys if keys is not None else list(secrets.keys())

    missing = [k for k in target_keys if k not in secrets]
    if missing:
        raise MaskError(f"Keys not found in vault: {', '.join(missing)}")

    results = []
    for key in target_keys:
        value = secrets[key]
        results.append(MaskedEntry(
            key=key,
            masked=_mask_value(value, reveal=reveal),
            length=len(value),
        ))
    return results


def format_masked(entries: list[MaskedEntry]) -> str:
    """Format masked entries for display."""
    if not entries:
        return "(no secrets)"
    return "\n".join(str(e) for e in entries)
