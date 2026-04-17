"""Promote secrets from one environment vault to another with optional key filtering."""
from __future__ import annotations
from pathlib import Path
from typing import Optional
from envault.vault import load_vault, save_vault, get_secret, set_secret, VaultError


class PromoteError(Exception):
    pass


def promote_secrets(
    src_path: Path,
    dst_path: Path,
    src_passphrase: str,
    dst_passphrase: str,
    keys: Optional[list[str]] = None,
    overwrite: bool = False,
) -> list[str]:
    """Copy secrets from src vault to dst vault. Returns list of promoted keys."""
    src = load_vault(src_path)
    dst = load_vault(dst_path)

    src_secrets = src.get("secrets", {})
    dst_secrets = dst.get("secrets", {})

    candidates = keys if keys is not None else list(src_secrets.keys())
    promoted = []

    for key in candidates:
        if key not in src_secrets:
            raise PromoteError(f"Key '{key}' not found in source vault")
        if key in dst_secrets and not overwrite:
            continue
        value = get_secret(src_path, src_passphrase, key)
        set_secret(dst_path, dst_passphrase, key, value)
        promoted.append(key)

    return promoted


def list_promote_candidates(
    src_path: Path,
    dst_path: Path,
    src_passphrase: str,
    dst_passphrase: str,
) -> dict[str, list[str]]:
    """Return keys grouped by: new (only in src), existing (in both)."""
    src = load_vault(src_path)
    dst = load_vault(dst_path)

    src_keys = set(src.get("secrets", {}).keys())
    dst_keys = set(dst.get("secrets", {}).keys())

    return {
        "new": sorted(src_keys - dst_keys),
        "existing": sorted(src_keys & dst_keys),
    }
