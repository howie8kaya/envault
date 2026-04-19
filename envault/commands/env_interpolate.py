"""Interpolate vault secrets into other secret values using ${KEY} syntax."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

from envault.vault import VaultError, load_vault, save_vault, get_secret, set_secret

_PLACEHOLDER_RE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")


class InterpolateError(Exception):
    pass


@dataclass
class InterpolateResult:
    """Result of an interpolation pass over the vault."""

    resolved: list[str] = field(default_factory=list)   # keys whose values changed
    skipped: list[str] = field(default_factory=list)    # keys with no placeholders
    unresolved: dict[str, list[str]] = field(default_factory=dict)  # key -> missing refs

    def __str__(self) -> str:  # pragma: no cover
        lines = []
        if self.resolved:
            lines.append(f"Resolved ({len(self.resolved)}): {', '.join(self.resolved)}")
        if self.unresolved:
            for key, missing in self.unresolved.items():
                lines.append(f"Unresolved {key}: missing {missing}")
        if not lines:
            lines.append("Nothing to interpolate.")
        return "\n".join(lines)


def _interpolate_value(value: str, lookup: dict[str, str]) -> tuple[str, list[str]]:
    """Replace ${KEY} placeholders in *value* using *lookup*.

    Returns the interpolated string and a list of any keys that were missing.
    """
    missing: list[str] = []

    def replacer(m: re.Match) -> str:
        ref = m.group(1)
        if ref in lookup:
            return lookup[ref]
        missing.append(ref)
        return m.group(0)  # leave placeholder intact

    interpolated = _PLACEHOLDER_RE.sub(replacer, value)
    return interpolated, missing


def interpolate_vault(
    vault_path: str,
    passphrase: str,
    *,
    keys: Optional[list[str]] = None,
    strict: bool = False,
) -> InterpolateResult:
    """Interpolate ${KEY} references inside vault secret values.

    Args:
        vault_path: Path to the vault file.
        passphrase: Vault passphrase.
        keys: Optional subset of keys to process; defaults to all keys.
        strict: If True, raise InterpolateError when a referenced key is missing.

    Returns:
        InterpolateResult summarising what changed.
    """
    vault = load_vault(vault_path)
    secrets = vault.get("secrets", {})

    # Decrypt all values first so we can resolve cross-references.
    plaintext: dict[str, str] = {}
    for k in secrets:
        try:
            plaintext[k] = get_secret(vault_path, passphrase, k)
        except VaultError as exc:
            raise InterpolateError(f"Could not decrypt '{k}': {exc}") from exc

    target_keys = keys if keys is not None else list(plaintext.keys())

    # Validate requested keys exist.
    for k in target_keys:
        if k not in plaintext:
            raise InterpolateError(f"Key '{k}' not found in vault.")

    result = InterpolateResult()

    for k in target_keys:
        original = plaintext[k]
        if not _PLACEHOLDER_RE.search(original):
            result.skipped.append(k)
            continue

        interpolated, missing = _interpolate_value(original, plaintext)

        if missing:
            if strict:
                raise InterpolateError(
                    f"Key '{k}' references undefined keys: {missing}"
                )
            result.unresolved[k] = missing
            continue

        if interpolated != original:
            set_secret(vault_path, passphrase, k, interpolated)
            result.resolved.append(k)

    return result


def preview_interpolation(
    vault_path: str,
    passphrase: str,
    keys: Optional[list[str]] = None,
) -> dict[str, str]:
    """Return a dict of key -> interpolated value without writing to the vault."""
    vault = load_vault(vault_path)
    secrets = vault.get("secrets", {})

    plaintext: dict[str, str] = {}
    for k in secrets:
        try:
            plaintext[k] = get_secret(vault_path, passphrase, k)
        except VaultError as exc:
            raise InterpolateError(f"Could not decrypt '{k}': {exc}") from exc

    target_keys = keys if keys is not None else list(plaintext.keys())
    preview: dict[str, str] = {}
    for k in target_keys:
        if k not in plaintext:
            raise InterpolateError(f"Key '{k}' not found in vault.")
        interpolated, _ = _interpolate_value(plaintext[k], plaintext)
        preview[k] = interpolated

    return preview
