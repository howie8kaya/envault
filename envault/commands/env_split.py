"""Split a vault into multiple vaults by prefix or key list."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from envault.vault import VaultError, init_vault, load_vault, set_secret


class SplitError(Exception):
    pass


@dataclass
class SplitResult:
    source_path: Path
    shards: Dict[str, Path] = field(default_factory=dict)  # label -> path
    counts: Dict[str, int] = field(default_factory=dict)

    def __str__(self) -> str:
        lines = [f"Split '{self.source_path.name}' into {len(self.shards)} shard(s):"]
        for label, path in self.shards.items():
            lines.append(f"  [{label}] {path.name} — {self.counts.get(label, 0)} key(s)")
        return "\n".join(lines)


def split_by_prefix(
    vault_path: Path,
    passphrase: str,
    prefix_map: Dict[str, Path],
    *,
    strip_prefix: bool = False,
    overwrite: bool = False,
) -> SplitResult:
    """Split secrets into separate vaults based on key prefixes.

    Args:
        vault_path: Source vault.
        passphrase: Passphrase for source vault.
        prefix_map: Mapping of prefix -> destination vault path.
        strip_prefix: If True, remove the prefix from keys in destination vaults.
        overwrite: If True, overwrite existing destination vaults.
    """
    data = load_vault(vault_path, passphrase)
    secrets: dict = data.get("secrets", {})

    result = SplitResult(source_path=vault_path)

    for prefix, dest_path in prefix_map.items():
        matching = {
            k: v for k, v in secrets.items() if k.startswith(prefix)
        }
        if not matching:
            continue

        init_vault(dest_path, passphrase, overwrite=overwrite)
        for key, ciphertext in matching.items():
            dest_key = key[len(prefix):] if strip_prefix else key
            if not dest_key:
                continue
            from envault.crypto import decrypt
            plaintext = decrypt(ciphertext, passphrase)
            set_secret(dest_path, passphrase, dest_key, plaintext)

        result.shards[prefix] = dest_path
        result.counts[prefix] = len(matching)

    return result


def split_by_map(
    vault_path: Path,
    passphrase: str,
    key_map: Dict[str, List[str]],
    dest_dir: Path,
    *,
    overwrite: bool = False,
) -> SplitResult:
    """Split specific keys into named vault shards.

    Args:
        vault_path: Source vault.
        passphrase: Passphrase for source vault.
        key_map: Mapping of shard label -> list of keys to include.
        dest_dir: Directory where shard vaults are created.
        overwrite: If True, overwrite existing shard vaults.
    """
    data = load_vault(vault_path, passphrase)
    secrets: dict = data.get("secrets", {})

    dest_dir.mkdir(parents=True, exist_ok=True)
    result = SplitResult(source_path=vault_path)

    for label, keys in key_map.items():
        dest_path = dest_dir / f"{label}.vault"
        init_vault(dest_path, passphrase, overwrite=overwrite)
        count = 0
        for key in keys:
            if key not in secrets:
                raise SplitError(f"Key '{key}' not found in vault")
            from envault.crypto import decrypt
            plaintext = decrypt(secrets[key], passphrase)
            set_secret(dest_path, passphrase, key, plaintext)
            count += 1
        result.shards[label] = dest_path
        result.counts[label] = count

    return result
