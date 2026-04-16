"""Compare secrets between two vault files."""
from __future__ import annotations
from dataclasses import dataclass
from typing import List
from envault.vault import load_vault, get_secret, VaultError


class CompareError(Exception):
    pass


@dataclass
class CompareEntry:
    key: str
    left_value: str | None
    right_value: str | None

    @property
    def status(self) -> str:
        if self.left_value is None:
            return "right_only"
        if self.right_value is None:
            return "left_only"
        if self.left_value != self.right_value:
            return "changed"
        return "same"

    def __str__(self) -> str:
        sym = {"same": "=", "changed": "~", "left_only": "<", "right_only": ">"}
        return f"{sym[self.status]} {self.key}"


def compare_vaults(
    left_path: str,
    left_passphrase: str,
    right_path: str,
    right_passphrase: str,
    show_same: bool = False,
) -> List[CompareEntry]:
    left_vault = load_vault(left_path)
    right_vault = load_vault(right_path)

    left_keys = set(left_vault.get("secrets", {}).keys())
    right_keys = set(right_vault.get("secrets", {}).keys())
    all_keys = sorted(left_keys | right_keys)

    results = []
    for key in all_keys:
        lv = rv = None
        if key in left_keys:
            try:
                lv = get_secret(left_vault, key, left_passphrase)
            except VaultError:
                lv = "<decrypt_error>"
        if key in right_keys:
            try:
                rv = get_secret(right_vault, key, right_passphrase)
            except VaultError:
                rv = "<decrypt_error>"
        entry = CompareEntry(key=key, left_value=lv, right_value=rv)
        if entry.status != "same" or show_same:
            results.append(entry)
    return results


def format_compare(entries: List[CompareEntry]) -> str:
    if not entries:
        return "Vaults are identical."
    lines = []
    for e in entries:
        if e.status == "changed":
            lines.append(f"~ {e.key}  (values differ)")
        elif e.status == "left_only":
            lines.append(f"< {e.key}  (only in left)")
        elif e.status == "right_only":
            lines.append(f"> {e.key}  (only in right)")
        else:
            lines.append(f"= {e.key}")
    return "\n".join(lines)
