"""Export all secrets belonging to a group as a .env snippet."""

from __future__ import annotations
from typing import Dict, List
from envault.vault import load_vault, VaultError
from envault.commands.group import _groups_meta, GroupError
from envault.crypto import decrypt
from envault.env_io import serialize_env


def export_group(vault_path, passphrase: str, group: str) -> str:
    """Return a .env-formatted string of all secrets in the group."""
    vault = load_vault(vault_path, passphrase)
    groups = _groups_meta(vault)
    if group not in groups:
        raise GroupError(f"Group '{group    keys = groups[group]
    secrets = vault.get("secrets", {})
    pairs: Dict[str, str] = {}
    for key in keys:
        if key not in secrets:
            continue
        pairs[key] = decrypt(secrets[key], passphrase)
    return serialize_env(pairs)


def group_summary(vault_path, passphrase: str) -> List[Dict]:
    """Return a list of dicts summarising each group."""
    vault = load_vault(vault_path, passphrase)
    groups = _groups_meta(vault)
    secrets = vault.get("secrets", {})
    result = []
    for name, keys in groups.items():
        present = [k for k in keys if k in secrets]
        missing = [k for k in keys if k not in secrets]
        result.append({
            "group": name,
            "count": len(present),
            "keys": present,
            "missing": missing,
        })
    return result
