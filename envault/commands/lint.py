"""Lint vault secrets for common issues like empty values, weak names, or duplicates."""

from dataclasses import dataclass, field
from typing import List

from envault.vault import load_vault, VaultError
from envault.crypto import decrypt


@dataclass
class LintIssue:
    key: str
    severity: str  # 'error' | 'warning' | 'info'
    message: str

    def __str__(self) -> str:
        icon = {"error": "✖", "warning": "⚠", "info": "ℹ"}.get(self.severity, "?")
        return f"  {icon} [{self.severity.upper()}] {self.key}: {self.message}"


_SUSPICIOUS_PATTERNS = ["todo", "fixme", "changeme", "placeholder", "example", "test"]
_WEAK_NAMES = ["secret", "password", "key", "token"]


def lint_vault(vault_path: str, passphrase: str) -> List[LintIssue]:
    """Decrypt vault and check secrets for common issues."""
    data = load_vault(vault_path)
    secrets: dict = data.get("secrets", {})

    issues: List[LintIssue] = []
    seen_values: dict = {}

    for key, ciphertext in secrets.items():
        try:
            value = decrypt(ciphertext, passphrase)
        except Exception:
            issues.append(LintIssue(key, "error", "failed to decrypt — passphrase may be wrong"))
            continue

        if not value.strip():
            issues.append(LintIssue(key, "error", "value is empty or blank"))
            continue

        if value in seen_values:
            issues.append(LintIssue(key, "warning", f"duplicate value shared with '{seen_values[value]}'"))
        else:
            seen_values[value] = key

        lower_val = value.lower()
        for pat in _SUSPICIOUS_PATTERNS:
            if pat in lower_val:
                issues.append(LintIssue(key, "warning", f"value looks like a placeholder (contains '{pat}')"))
                break

        if key.upper() in [n.upper() for n in _WEAK_NAMES]:
            issues.append(LintIssue(key, "info", "key name is very generic; consider a more descriptive name"))

        if len(value) < 8:
            issues.append(LintIssue(key, "warning", "value is very short (< 8 chars)"))

    return issues


def format_lint_results(issues: List[LintIssue], total_keys: int) -> str:
    if not issues:
        return f"✔ No issues found across {total_keys} secret(s)."
    lines = [f"Found {len(issues)} issue(s) in {total_keys} secret(s):\n"]
    lines.extend(str(i) for i in issues)
    return "\n".join(lines)
