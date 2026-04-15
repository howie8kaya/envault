"""Search secrets in a vault by key pattern or value substring."""

from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass
from typing import List, Optional

from envault.vault import load_vault, get_secret


@dataclass
class SearchResult:
    key: str
    value: str
    match_type: str  # 'key' | 'value' | 'both'

    def __str__(self) -> str:
        masked = self.value[:4] + "****" if len(self.value) > 4 else "****"
        return f"[{self.match_type}] {self.key}={masked}"


def search_vault(
    vault_path: str,
    passphrase: str,
    pattern: str,
    *,
    search_values: bool = False,
    glob_mode: bool = False,
    case_sensitive: bool = False,
) -> List[SearchResult]:
    """Search vault secrets by key pattern and optionally by value.

    Args:
        vault_path: Path to the .vault file.
        passphrase: Vault passphrase for decryption.
        pattern: Search pattern (substring, glob, or regex depending on flags).
        search_values: Also search inside decrypted values.
        glob_mode: Treat pattern as a glob expression (e.g. DB_*).
        case_sensitive: Whether matching is case-sensitive.

    Returns:
        List of SearchResult objects for every matching secret.
    """
    vault = load_vault(vault_path)
    keys: list[str] = list(vault.get("secrets", {}).keys())

    flags = 0 if case_sensitive else re.IGNORECASE

    def _matches_key(key: str) -> bool:
        if glob_mode:
            return fnmatch.fnmatchcase(key if case_sensitive else key.lower(),
                                       pattern if case_sensitive else pattern.lower())
        return bool(re.search(pattern, key, flags))

    def _matches_value(val: str) -> bool:
        if glob_mode:
            return fnmatch.fnmatchcase(val if case_sensitive else val.lower(),
                                       pattern if case_sensitive else pattern.lower())
        return bool(re.search(pattern, val, flags))

    results: List[SearchResult] = []
    for key in keys:
        value = get_secret(vault_path, key, passphrase)
        key_hit = _matches_key(key)
        val_hit = search_values and _matches_value(value)

        if key_hit and val_hit:
            results.append(SearchResult(key=key, value=value, match_type="both"))
        elif key_hit:
            results.append(SearchResult(key=key, value=value, match_type="key"))
        elif val_hit:
            results.append(SearchResult(key=key, value=value, match_type="value"))

    return results


def format_search_results(results: List[SearchResult], *, reveal: bool = False) -> str:
    """Format search results for CLI output."""
    if not results:
        return "No matches found."
    lines = []
    for r in results:
        if reveal:
            lines.append(f"[{r.match_type}] {r.key}={r.value}")
        else:
            lines.append(str(r))
    return "\n".join(lines)
