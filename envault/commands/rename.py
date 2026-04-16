"""Rename a secret key inside a vault."""

from envault.vault import load_vault, save_vault, VaultError
from envault.commands.audit import record_event


class RenameError(Exception):
    pass


def rename_secret(vault_path, old_key: str, new_key: str, passphrase: str) -> None:
    """Rename a secret key from old_key to new_key.

    Raises RenameError if old_key does not exist or new_key already exists.
    """
    vault = load_vault(vault_path, passphrase)
    secrets = vault.get("secrets", {})

    if old_key not in secrets:
        raise RenameError(f"Key '{old_key}' not found in vault.")

    if new_key in secrets:
        raise RenameError(f"Key '{new_key}' already exists in vault.")

    secrets[new_key] = secrets.pop(old_key)
    vault["secrets"] = secrets
    save_vault(vault_path, vault, passphrase)
    record_event(vault_path, "rename", {"old_key": old_key, "new_key": new_key})


def list_rename_candidates(vault_path, passphrase: str) -> list[str]:
    """Return all secret keys available for renaming."""
    vault = load_vault(vault_path, passphrase)
    return sorted(vault.get("secrets", {}).keys())
