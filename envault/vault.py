"""Vault module for reading, writing, and managing encrypted .env vault files."""

import json
import os
from typing import Optional

from envault.crypto import encrypt, decrypt

DEFAULT_VAULT_FILE = ".envault"


class VaultError(Exception):
    pass


def load_vault(vault_path: str, passphrase: str) -> dict:
    """Load and decrypt a vault file, returning the env dict."""
    path = Path(vault_path)
    if not path.exists():
        raise VaultError(f"Vault file not found: {vault_path}")

    ciphertext = path.read_text(encoding="utf-8").strip()
    try:
        plaintext = decrypt(ciphertext, passphrase)
    except Exception as e:
        raise VaultError(f"Failed to decrypt vault: {e}") from e

    try:
        return json.loads(plaintext)
    except json.JSONDecodeError as e:
        raise VaultError(f"Vault contents are not valid JSON: {e}") from e


def save_vault(vault_path: str, passphrase: str, env_data: dict) -> None:
    """Encrypt and save env dict to a vault file."""
    plaintext = json.dumps(env_data, indent=2)
    ciphertext = encrypt(plaintext, passphrase)
    Path(vault_path).write_text(ciphertext + "\n", encoding="utf-8")


def init_vault(vault_path: str, passphrase: str, overwrite: bool = False) -> None:
    """Create a new empty vault file."""
    path = Path(vault_path)
    if path.exists() and not overwrite:
        raise VaultError(f"Vault already exists: {vault_path}. Use overwrite=True to replace it.")
    save_vault(vault_path, passphrase, {})


def set_secret(vault_path: str, passphrase: str, key: str, value: str) -> None:
    """Add or update a key-value pair in the vault."""
    env_data = load_vault(vault_path, passphrase) if Path(vault_path).exists() else {}
    env_data[key] = value
    save_vault(vault_path, passphrase, env_data)


def get_secret(vault_path: str, passphrase: str, key: str) -> Optional[str]:
    """Retrieve a single secret from the vault by key."""
    env_data = load_vault(vault_path, passphrase)
    return env_data.get(key)


def delete_secret(vault_path: str, passphrase: str, key: str) -> bool:
    """Remove a key from the vault. Returns True if key existed."""
    env_data = load_vault(vault_path, passphrase)
    if key not in env_data:
        return False
    del env_data[key]
    save_vault(vault_path, passphrase, env_data)
    return True


def export_dotenv(vault_path: str, passphrase: str, output_path: str) -> None:
    """Export vault contents as a plain .env file."""
    env_data = load_vault(vault_path, passphrase)
    lines = [f'{k}={v}\n' for k, v in env_data.items()]
    Path(output_path).write_text("".join(lines), encoding="utf-8")
