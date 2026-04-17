"""Validate vault secrets against expected types and formats."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

from envault.vault import load_vault, decrypt_secret, VaultError


TYPE_PATTERNS = {
    "url": re.compile(r"^https?://[^\s]+$"),
    "email": re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$"),
    "integer": re.compile(r"^-?\d+$"),
    "boolean": re.compile(r"^(true|false|1|0|yes|no)$", re.IGNORECASE),
    "uuid": re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE),
    "hex": re.compile(r"^[0-9a-fA-F]+$"),
    "nonempty": re.compile(r".+"),
}


class EnvValidateError(Exception):
    pass


@dataclass
class ValidationResult:
    key: str
    expected_type: str
    value_preview: str
    passed: bool
    message: str

    def __str__(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        return f"[{status}] {self.key} ({self.expected_type}): {self.message}"


def validate_type(value: str, type_name: str) -> bool:
    pattern = TYPE_PATTERNS.get(type_name)
    if pattern is None:
        raise EnvValidateError(f"Unknown type: '{type_name}'. Valid types: {list(TYPE_PATTERNS)}")
    return bool(pattern.match(value))


def validate_vault_types(
    vault_path,
    passphrase: str,
    rules: dict[str, str],
) -> list[ValidationResult]:
    """Validate decrypted vault secrets against type rules.

    Args:
        vault_path: Path to the vault file.
        passphrase: Vault passphrase.
        rules: Mapping of key -> type_name.

    Returns:
        List of ValidationResult for each rule.
    """
    vault = load_vault(vault_path)
    results = []

    for key, type_name in rules.items():
        if key not in vault.get("secrets", {}):
            results.append(ValidationResult(
                key=key,
                expected_type=type_name,
                value_preview="",
                passed=False,
                message="Key not found in vault",
            ))
            continue

        try:
            value = decrypt_secret(vault, key, passphrase)
        except VaultError as e:
            results.append(ValidationResult(
                key=key,
                expected_type=type_name,
                value_preview="",
                passed=False,
                message=f"Decryption failed: {e}",
            ))
            continue

        preview = value[:6] + "..." if len(value) > 6 else value
        try:
            passed = validate_type(value, type_name)
        except EnvValidateError as e:
            results.append(ValidationResult(
                key=key, expected_type=type_name, value_preview=preview,
                passed=False, message=str(e)
            ))
            continue

        message = "OK" if passed else f"Value does not match type '{type_name}'"
        results.append(ValidationResult(
            key=key, expected_type=type_name, value_preview=preview,
            passed=passed, message=message
        ))

    return results


def format_validation_results(results: list[ValidationResult]) -> str:
    if not results:
        return "No rules to validate."
    return "\n".join(str(r) for r in results)
