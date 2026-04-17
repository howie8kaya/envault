"""Schema validation for vault secrets."""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Optional
from envault.vault import load_vault, VaultError


class SchemaError(Exception):
    pass


@dataclass
class SchemaRule:
    key: str
    required: bool = True
    pattern: Optional[str] = None
    min_length: int = 0
    max_length: int = 0  # 0 = unlimited


@dataclass
class ValidationIssue:
    key: str
    severity: str  # 'error' | 'warning'
    message: str

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] {self.key}: {self.message}"


def validate_vault(vault_path: str, passphrase: str, rules: list[SchemaRule]) -> list[ValidationIssue]:
    """Validate vault secrets against a list of schema rules."""
    from envault.vault import get_secret
    vault = load_vault(vault_path)
    issues: list[ValidationIssue] = []

    for rule in rules:
        try:
            value = get_secret(vault, rule.key, passphrase)
        except VaultError:
            value = None

        if value is None:
            if rule.required:
                issues.append(ValidationIssue(rule.key, "error", "required key is missing"))
            continue

        if rule.min_length and len(value) < rule.min_length:
            issues.append(ValidationIssue(rule.key, "error",
                f"value too short (min {rule.min_length}, got {len(value)})"))

        if rule.max_length and len(value) > rule.max_length:
            issues.append(ValidationIssue(rule.key, "error",
                f"value too long (max {rule.max_length}, got {len(value)})"))

        if rule.pattern and not re.fullmatch(rule.pattern, value):
            issues.append(ValidationIssue(rule.key, "error",
                f"value does not match pattern '{rule.pattern}'"))

    return issues


def format_schema_results(issues: list[ValidationIssue]) -> str:
    if not issues:
        return "Schema validation passed."
    return "\n".join(str(i) for i in issues)
