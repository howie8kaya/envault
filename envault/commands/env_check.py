"""Check which vault secrets are missing from the current environment."""
from __future__ import annotations
import os
from dataclasses import dataclass, field
from typing import List, Optional
from envault.vault import load_vault, VaultError


class EnvCheckError(Exception):
    pass


@dataclass
class CheckResult:
    key: str
    expected: bool  # True = key should exist in env
    found: bool
    env_value: Optional[str] = None

    def __str__(self) -> str:
        status = "OK" if self.found else "MISSING"
        return f"[{status}] {self.key}"


def check_env(vault_path: str, passphrase: str, keys: Optional[List[str]] = None) -> List[CheckResult]:
    """Compare vault keys against os.environ, return check results."""
    try:
        vault = load_vault(vault_path, passphrase)
    except VaultError as e:
        raise EnvCheckError(str(e)) from e

    secrets = vault.get("secrets", {})
    target_keys = keys if keys else list(secrets.keys())

    results: List[CheckResult] = []
    for key in target_keys:
        if key not in secrets:
            raise EnvCheckError(f"Key '{key}' not found in vault")
        env_val = os.environ.get(key)
        results.append(CheckResult(
            key=key,
            expected=True,
            found=env_val is not None,
            env_value=env_val,
        ))
    return results


def missing_keys(results: List[CheckResult]) -> List[str]:
    """Return list of keys that are missing from the environment."""
    return [r.key for r in results if not r.found]


def format_check_results(results: List[CheckResult]) -> str:
    lines = [str(r) for r in results]
    total = len(results)
    found = sum(1 for r in results if r.found)
    lines.append(f"\n{found}/{total} keys present in environment.")
    return "\n".join(lines)
