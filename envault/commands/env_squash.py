"""env_squash: Remove duplicate values from a vault, keeping only the first key found."""

from dataclasses import dataclass, field
from typing import List, Tuple

from envault.vault import VaultError, load_vault, save_vault, get_secret, set_secret, delete_secret


class SquashError(Exception):
    pass


@dataclass
class SquashResult:
    removed: List[Tuple[str, str]] = field(default_factory=list)  # (key, kept_key)
    kept: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        lines = []
        for key, kept in self.removed:
            lines.append(f"- {key} (duplicate of {kept})")
        if not lines:
            return "No duplicate values found."
        return "Squashed duplicates:\n" + "\n".join(lines)


def squash_vault(vault_path: str, passphrase: str, dry_run: bool = False) -> SquashResult:
    """Remove keys whose decrypted value duplicates an already-seen value.

    The first key encountered for a given value is kept; subsequent ones are removed.
    Keys are processed in sorted order for determinism.
    """
    vault = load_vault(vault_path)
    secrets = vault.get("secrets", {})

    if not secrets:
        return SquashResult()

    seen: dict = {}  # value -> first key that had it
    result = SquashResult()

    for key in sorted(secrets.keys()):
        try:
            value = get_secret(vault_path, key, passphrase)
        except VaultError as exc:
            raise SquashError(f"Could not decrypt '{key}': {exc}") from exc

        if value in seen:
            result.removed.append((key, seen[value]))
        else:
            seen[value] = key
            result.kept.append(key)

    if not dry_run:
        for key, _ in result.removed:
            delete_secret(vault_path, key, passphrase)

    return result


def list_squash_candidates(vault_path: str, passphrase: str) -> SquashResult:
    """Dry-run squash to preview what would be removed."""
    return squash_vault(vault_path, passphrase, dry_run=True)
