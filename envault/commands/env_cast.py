"""Cast vault secrets to typed Python values."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from envault.vault import load_vault, VaultError
from envault.crypto import decrypt


class CastError(Exception):
    pass


SUPPORTED_TYPES = ("str", "int", "float", "bool", "list")


@dataclass
class CastResult:
    key: str
    raw: str
    cast_type: str
    value: Any

    def __str__(self) -> str:
        return f"{self.key} ({self.cast_type}): {self.value!r}"


def _cast_value(raw: str, cast_type: str) -> Any:
    if cast_type == "str":
        return raw
    if cast_type == "int":
        try:
            return int(raw)
        except ValueError:
            raise CastError(f"Cannot cast {raw!r} to int")
    if cast_type == "float":
        try:
            return float(raw)
        except ValueError:
            raise CastError(f"Cannot cast {raw!r} to float")
    if cast_type == "bool":
        if raw.lower() in ("1", "true", "yes", "on"):
            return True
        if raw.lower() in ("0", "false", "no", "off"):
            return False
        raise CastError(f"Cannot cast {raw!r} to bool")
    if cast_type == "list":
        return [item.strip() for item in raw.split(",") if item.strip()]
    raise CastError(f"Unsupported type: {cast_type!r}. Choose from {SUPPORTED_TYPES}")


def cast_secret(vault_path: str, passphrase: str, key: str, cast_type: str) -> CastResult:
    data = load_vault(vault_path)
    if key not in data["secrets"]:
        raise CastError(f"Key {key!r} not found in vault")
    if cast_type not in SUPPORTED_TYPES:
        raise CastError(f"Unsupported type: {cast_type!r}")
    raw = decrypt(data["secrets"][key], passphrase)
    value = _cast_value(raw, cast_type)
    return CastResult(key=key, raw=raw, cast_type=cast_type, value=value)


def cast_all(vault_path: str, passphrase: str, type_map: dict[str, str]) -> list[CastResult]:
    """Cast multiple keys using a {key: type} mapping."""
    results = []
    for key, cast_type in type_map.items():
        results.append(cast_secret(vault_path, passphrase, key, cast_type))
    return results
