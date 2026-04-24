"""env_chain.py — resolve a sequence of vaults into a merged env layer.

Later vaults in the chain take precedence over earlier ones.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from envault.vault import load_vault, get_secret, VaultError


class ChainError(Exception):
    pass


@dataclass
class ChainResult:
    merged: Dict[str, str] = field(default_factory=dict)
    sources: Dict[str, str] = field(default_factory=dict)  # key -> vault path
    chain: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        lines = [f"Chain ({len(self.chain)} vaults, {len(self.merged)} keys):"]
        for key, value in sorted(self.merged.items()):
            lines.append(f"  {key}={value!r}  [{self.sources[key]}]")
        return "\n".join(lines)


def resolve_chain(
    vault_paths: List[Path],
    passphrases: List[str],
    keys: Optional[List[str]] = None,
) -> ChainResult:
    """Merge secrets from multiple vaults; later entries win on conflict."""
    if len(vault_paths) != len(passphrases):
        raise ChainError("vault_paths and passphrases must be the same length")
    if not vault_paths:
        raise ChainError("at least one vault path is required")

    merged: Dict[str, str] = {}
    sources: Dict[str, str] = {}

    for vault_path, passphrase in zip(vault_paths, passphrases):
        try:
            vault = load_vault(vault_path, passphrase)
        except VaultError as exc:
            raise ChainError(f"failed to load {vault_path}: {exc}") from exc

        candidates = keys if keys is not None else list(vault.get("secrets", {}).keys())
        for key in candidates:
            try:
                value = get_secret(vault_path, passphrase, key)
                merged[key] = value
                sources[key] = str(vault_path)
            except VaultError:
                pass  # key not present in this vault — skip

    return ChainResult(
        merged=merged,
        sources=sources,
        chain=[str(p) for p in vault_paths],
    )


def list_chain_candidates(vault_paths: List[Path], passphrases: List[str]) -> List[str]:
    """Return the union of all keys across every vault in the chain."""
    seen: List[str] = []
    for vault_path, passphrase in zip(vault_paths, passphrases):
        try:
            vault = load_vault(vault_path, passphrase)
            for key in vault.get("secrets", {}):
                if key not in seen:
                    seen.append(key)
        except VaultError:
            pass
    return seen
