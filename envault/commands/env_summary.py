"""env_summary.py — Generate a human-readable summary report of a vault."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from envault.vault import load_vault, decrypt_secret, VaultError


class SummaryError(Exception):
    pass


@dataclass
class SummaryEntry:
    key: str
    length: int
    is_empty: bool
    preview: str

    def __str__(self) -> str:
        status = "EMPTY" if self.is_empty else f"{self.length} chars"
        return f"  {self.key:<30} {status:<12} preview={self.preview}"


@dataclass
class VaultSummary:
    vault_path: str
    total_keys: int
    empty_keys: int
    avg_length: float
    entries: List[SummaryEntry] = field(default_factory=list)

    def __str__(self) -> str:
        lines = [
            f"Vault : {self.vault_path}",
            f"Keys  : {self.total_keys}",
            f"Empty : {self.empty_keys}",
            f"Avg   : {self.avg_length:.1f} chars",
            "-" * 55,
        ]
        for entry in self.entries:
            lines.append(str(entry))
        return "\n".join(lines)


def _preview(value: str, reveal: int = 4) -> str:
    if not value:
        return ""
    visible = value[:reveal]
    return visible + "*" * max(0, len(value) - reveal)


def summarize_vault(
    vault_path: str,
    passphrase: str,
    keys: Optional[List[str]] = None,
) -> VaultSummary:
    """Return a VaultSummary for the given vault."""
    vault = load_vault(vault_path)
    secrets: dict = vault.get("secrets", {})

    target_keys = keys if keys is not None else list(secrets.keys())
    missing = [k for k in target_keys if k not in secrets]
    if missing:
        raise SummaryError(f"Keys not found in vault: {', '.join(missing)}")

    entries: List[SummaryEntry] = []
    total_length = 0
    empty_count = 0

    for key in sorted(target_keys):
        value = decrypt_secret(secrets[key], passphrase)
        length = len(value)
        is_empty = length == 0
        total_length += length
        if is_empty:
            empty_count += 1
        entries.append(SummaryEntry(
            key=key,
            length=length,
            is_empty=is_empty,
            preview=_preview(value),
        ))

    avg = total_length / len(entries) if entries else 0.0

    return VaultSummary(
        vault_path=vault_path,
        total_keys=len(entries),
        empty_keys=empty_count,
        avg_length=avg,
        entries=entries,
    )
