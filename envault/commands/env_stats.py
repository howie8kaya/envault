"""Vault statistics and summary reporting."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
from envault.vault import load_vault, decrypt_secret, VaultError


class StatsError(Exception):
    pass


@dataclass
class VaultStats:
    total_keys: int = 0
    empty_values: int = 0
    short_values: int = 0  # < 8 chars
    long_values: int = 0   # >= 32 chars
    avg_value_length: float = 0.0
    keys: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        lines = [
            f"Total keys     : {self.total_keys}",
            f"Empty values   : {self.empty_values}",
            f"Short values   : {self.short_values} (< 8 chars)",
            f"Long values    : {self.long_values} (>= 32 chars)",
            f"Avg value len  : {self.avg_value_length:.1f}",
        ]
        return "\n".join(lines)


def vault_stats(vault_path: str, passphrase: str) -> VaultStats:
    """Compute statistics for all secrets in the vault."""
    try:
        data = load_vault(vault_path)
    except Exception as e:
        raise StatsError(f"Failed to load vault: {e}") from e

    secrets: dict = data.get("secrets", {})
    if not secrets:
        return VaultStats()

    lengths = []
    empty = 0
    short = 0
    long_ = 0
    keys = list(secrets.keys())

    for key in keys:
        try:
            value = decrypt_secret(data, key, passphrase)
        except Exception as e:
            raise StatsError(f"Failed to decrypt '{key}': {e}") from e
        n = len(value)
        lengths.append(n)
        if n == 0:
            empty += 1
        elif n < 8:
            short += 1
        if n >= 32:
            long_ += 1

    avg = sum(lengths) / len(lengths) if lengths else 0.0

    return VaultStats(
        total_keys=len(keys),
        empty_values=empty,
        short_values=short,
        long_values=long_,
        avg_value_length=avg,
        keys=keys,
    )
