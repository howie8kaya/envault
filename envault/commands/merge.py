"""Merge secrets from one vault into another."""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional
from envault.vault import load_vault, save_vault, get_secret, set_secret, VaultError


class MergeError(Exception):
    pass


@dataclass
class MergeResult:
    key: str
    action: str  # 'added', 'updated', 'skipped'

    def __str__(self) -> str:
        symbols = {'added': '+', 'updated': '~', 'skipped': '='}
        return f"{symbols.get(self.action, '?')} {self.key} ({self.action})"


def merge_vaults(
    src_path: str,
    src_passphrase: str,
    dst_path: str,
    dst_passphrase: str,
    keys: Optional[List[str]] = None,
    overwrite: bool = False,
) -> List[MergeResult]:
    """Merge secrets from src vault into dst vault.

    Args:
        src_path: Path to source vault file.
        src_passphrase: Passphrase for source vault.
        dst_path: Path to destination vault file.
        dst_passphrase: Passphrase for destination vault.
        keys: Optional list of keys to merge; merges all if None.
        overwrite: If True, overwrite existing keys in dst.

    Returns:
        List of MergeResult entries describing each key's fate.
    """
    src_vault = load_vault(src_path, src_passphrase)
    dst_vault = load_vault(dst_path, dst_passphrase)

    src_secrets: dict = src_vault.get("secrets", {})
    dst_secrets: dict = dst_vault.get("secrets", {})

    candidate_keys = keys if keys is not None else list(src_secrets.keys())

    missing = [k for k in candidate_keys if k not in src_secrets]
    if missing:
        raise MergeError(f"Keys not found in source vault: {', '.join(missing)}")

    results: List[MergeResult] = []
    for key in candidate_keys:
        value = get_secret(src_vault, key, src_passphrase)
        if key in dst_secrets and not overwrite:
            results.append(MergeResult(key=key, action="skipped"))
        else:
            action = "updated" if key in dst_secrets else "added"
            set_secret(dst_vault, key, value, dst_passphrase)
            results.append(MergeResult(key=key, action=action))

    save_vault(dst_path, dst_vault, dst_passphrase)
    return results


def format_merge_results(results: List[MergeResult]) -> str:
    if not results:
        return "Nothing to merge."
    lines = [str(r) for r in results]
    summary_counts = {"added": 0, "updated": 0, "skipped": 0}
    for r in results:
        summary_counts[r.action] = summary_counts.get(r.action, 0) + 1
    lines.append(
        f"\nSummary: {summary_counts['added']} added, "
        f"{summary_counts['updated']} updated, {summary_counts['skipped']} skipped."
    )
    return "\n".join(lines)
