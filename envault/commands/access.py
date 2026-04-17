"""Access control — restrict which keys a given role/user can read."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from envault.vault import load_vault, VaultError


class AccessError(Exception):
    pass


def _access_meta(vault_path: Path) -> Path:
    return vault_path.with_suffix(".access.json")


def set_access(vault_path: Path, role: str, keys: List[str]) -> Dict[str, List[str]]:
    """Grant *role* access to *keys*. Replaces any existing grant for that role."""
    vault = load_vault(vault_path)
    for key in keys:
        if key not in vault["secrets"]:
            raise AccessError(f"Key not found in vault: {key}")

    meta_path = _access_meta(vault_path)
    meta: Dict[str, List[str]] = json.loads(meta_path.read_text()) if meta_path.exists() else {}
    meta[role] = list(keys)
    meta_path.write_text(json.dumps(meta, indent=2))
    return meta


def get_access(vault_path: Path, role: str) -> Optional[List[str]]:
    """Return the list of keys *role* can access, or None if no rule set."""
    meta_path = _access_meta(vault_path)
    if not meta_path.exists():
        return None
    meta: Dict[str, List[str]] = json.loads(meta_path.read_text())
    return meta.get(role)


def revoke_access(vault_path: Path, role: str) -> bool:
    """Remove access rules for *role*. Returns True if a rule existed."""
    meta_path = _access_meta(vault_path)
    if not meta_path.exists():
        return False
    meta: Dict[str, List[str]] = json.loads(meta_path.read_text())
    existed = role in meta
    meta.pop(role, None)
    meta_path.write_text(json.dumps(meta, indent=2))
    return existed


def list_roles(vault_path: Path) -> List[str]:
    """Return all roles that have access rules defined."""
    meta_path = _access_meta(vault_path)
    if not meta_path.exists():
        return []
    meta: Dict[str, List[str]] = json.loads(meta_path.read_text())
    return list(meta.keys())


def filter_by_role(vault_path: Path, passphrase: str, role: str) -> Dict[str, str]:
    """Decrypt and return only the secrets accessible to *role*."""
    from envault.vault import get_secret

    allowed = get_access(vault_path, role)
    if allowed is None:
        raise AccessError(f"No access rules defined for role: {role}")
    result: Dict[str, str] = {}
    for key in allowed:
        result[key] = get_secret(vault_path, key, passphrase)
    return result
