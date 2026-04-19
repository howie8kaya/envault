"""env_defaults.py — fill in missing vault keys from a defaults file or dict."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from envault.vault import load_vault, save_vault, set_secret, VaultError
from envault.env_io import parse_env, read_env_file


class DefaultsError(Exception):
    pass


@dataclass
class DefaultsResult:
    applied: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        lines = []
        for k in self.applied:
            lines.append(f"  + {k} (applied)")
        for k in self.skipped:
            lines.append(f"  ~ {k} (skipped, already set)")
        return "\n".join(lines) if lines else "  (no changes)"


def apply_defaults(
    vault_path: Path,
    passphrase: str,
    defaults: dict[str, str],
    overwrite: bool = False,
) -> DefaultsResult:
    """Apply default key/value pairs to the vault, skipping existing keys unless overwrite=True."""
    data = load_vault(vault_path, passphrase)
    result = DefaultsResult()

    for key, value in defaults.items():
        if key in data and not overwrite:
            result.skipped.append(key)
        else:
            set_secret(vault_path, passphrase, key, value)
            result.applied.append(key)

    return result


def apply_defaults_from_file(
    vault_path: Path,
    passphrase: str,
    defaults_file: Path,
    overwrite: bool = False,
) -> DefaultsResult:
    """Load defaults from a .env file and apply them to the vault."""
    if not defaults_file.exists():
        raise DefaultsError(f"Defaults file not found: {defaults_file}")
    try:
        raw = read_env_file(defaults_file)
        defaults = parse_env(raw)
    except Exception as exc:
        raise DefaultsError(f"Failed to parse defaults file: {exc}") from exc

    return apply_defaults(vault_path, passphrase, defaults, overwrite=overwrite)


def list_defaults_candidates(vault_path: Path, passphrase: str, defaults: dict[str, str]) -> list[str]:
    """Return keys from defaults that are NOT yet in the vault."""
    data = load_vault(vault_path, passphrase)
    return [k for k in defaults if k not in data]
