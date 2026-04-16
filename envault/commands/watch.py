"""Watch a .env file for changes and sync to vault automatically."""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

from envault.env_io import read_env_file
from envault.vault import load_vault, set_secret, save_vault


class WatchError(Exception):
    pass


@dataclass
class WatchEvent:
    path: Path
    changed_keys: list[str]
    timestamp: float = field(default_factory=time.time)

    def __str__(self) -> str:
        keys = ", ".join(self.changed_keys)
        return f"[{self.path.name}] changed keys: {keys}"


def _file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sync_changes(
    env_path: Path,
    vault_path: Path,
    passphrase: str,
    prev_env: dict[str, str],
) -> tuple[list[str], dict[str, str]]:
    """Sync env file changes to vault. Returns (changed_keys, new_env)."""
    new_env = read_env_file(env_path)
    changed = [
        k for k, v in new_env.items()
        if prev_env.get(k) != v
    ]
    if changed:
        vault = load_vault(vault_path, passphrase)
        for key in changed:
            set_secret(vault, key, new_env[key], passphrase)
        save_vault(vault_path, vault)
    return changed, new_env


def watch_env_file(
    env_path: Path,
    vault_path: Path,
    passphrase: str,
    interval: float = 1.0,
    on_change: Optional[Callable[[WatchEvent], None]] = None,
    max_iterations: Optional[int] = None,
) -> None:
    """Poll env_path and sync changes to vault. Blocks until interrupted."""
    if not env_path.exists():
        raise WatchError(f"File not found: {env_path}")
    if not vault_path.exists():
        raise WatchError(f"Vault not found: {vault_path}")

    current_hash = _file_hash(env_path)
    current_env = read_env_file(env_path)
    iterations = 0

    try:
        while True:
            if max_iterations is not None and iterations >= max_iterations:
                break
            time.sleep(interval)
            iterations += 1
            new_hash = _file_hash(env_path)
            if new_hash != current_hash:
                changed, current_env = _sync_changes(
                    env_path, vault_path, passphrase, current_env
                )
                current_hash = new_hash
                if changed and on_change:
                    on_change(WatchEvent(path=env_path, changed_keys=changed))
    except KeyboardInterrupt:
        pass
