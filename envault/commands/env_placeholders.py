"""Detect and report unresolved placeholder values in a vault."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional

from envault.vault import load_vault, VaultError
from envault.crypto import decrypt

PLACEHOLDER_PATTERN = re.compile(r"^<.+>$|^\{\{.+\}\}$|^CHANGE_ME$|^TODO$|^FIXME$", re.IGNORECASE)


class PlaceholderError(Exception):
    pass


@dataclass
class PlaceholderEntry:
    key: str
    value: str
    pattern_matched: str

    def __str__(self) -> str:
        return f"{self.key}: {self.value!r} (matched: {self.pattern_matched})"


@dataclass
class PlaceholderResult:
    total_keys: int
    entries: List[PlaceholderEntry] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.entries)

    @property
    def clean(self) -> bool:
        return len(self.entries) == 0

    def __str__(self) -> str:
        if self.clean:
            return f"No placeholders found ({self.total_keys} keys checked)."
        lines = [f"{self.count} placeholder(s) found ({self.total_keys} keys checked):"]
        for e in self.entries:
            lines.append(f"  - {e}")
        return "\n".join(lines)


def _detect_placeholder(value: str) -> Optional[str]:
    """Return the matched pattern description if value looks like a placeholder."""
    if PLACEHOLDER_PATTERN.match(value.strip()):
        return value.strip()
    return None


def find_placeholders(
    vault_path: str,
    passphrase: str,
    keys: Optional[List[str]] = None,
) -> PlaceholderResult:
    """Scan vault secrets for unresolved placeholder values."""
    vault = load_vault(vault_path)
    secrets: dict = vault.get("secrets", {})

    if keys is not None:
        missing = [k for k in keys if k not in secrets]
        if missing:
            raise PlaceholderError(f"Keys not found in vault: {', '.join(missing)}")
        target = {k: secrets[k] for k in keys}
    else:
        target = secrets

    entries: List[PlaceholderEntry] = []
    for key, ciphertext in target.items():
        try:
            value = decrypt(ciphertext, passphrase)
        except Exception:
            continue
        matched = _detect_placeholder(value)
        if matched is not None:
            entries.append(PlaceholderEntry(key=key, value=value, pattern_matched=matched))

    return PlaceholderResult(total_keys=len(target), entries=entries)
