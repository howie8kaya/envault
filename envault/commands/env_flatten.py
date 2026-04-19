"""Flatten nested JSON/dict values stored in vault secrets into individual keys."""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from typing import Optional
from envault.vault import load_vault, save_vault, set_secret, get_secret, VaultError


class FlattenError(Exception):
    pass


@dataclass
class FlattenResult:
    flattened: dict[str, str] = field(default_factory=dict)  # new_key -> value
    skipped: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        lines = []
        for k, v in self.flattened.items():
            lines.append(f"  + {k} = {v}")
        for k in self.skipped:
            lines.append(f"  ~ {k} (skipped, not JSON object)")
        return "\n".join(lines) if lines else "  (nothing to flatten)"


def _flatten_dict(d: dict, prefix: str, sep: str) -> dict[str, str]:
    result = {}
    for k, v in d.items():
        new_key = f"{prefix}{sep}{k}" if prefix else k
        if isinstance(v, dict):
            result.update(_flatten_dict(v, new_key, sep))
        else:
            result[new_key] = str(v)
    return result


def flatten_secret(
    vault_path: str,
    passphrase: str,
    key: str,
    sep: str = "__",
    prefix: Optional[str] = None,
    overwrite: bool = False,
) -> FlattenResult:
    """Expand a JSON-object secret into multiple flat keys."""
    vault = load_vault(vault_path, passphrase)
    raw = get_secret(vault, passphrase, key)
    try:
        parsed = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        raise FlattenError(f"Secret '{key}' is not valid JSON")
    if not isinstance(parsed, dict):
        raise FlattenError(f"Secret '{key}' must be a JSON object, got {type(parsed).__name__}")

    base = prefix if prefix is not None else key
    flat = _flatten_dict(parsed, base, sep)

    result = FlattenResult()
    for new_key, value in flat.items():
        existing = vault.get("secrets", {}).get(new_key)
        if existing and not overwrite:
            result.skipped.append(new_key)
            continue
        vault = set_secret(vault, passphrase, new_key, value)
        result.flattened[new_key] = value

    save_vault(vault_path, vault)
    return result
