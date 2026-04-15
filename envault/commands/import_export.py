"""Commands for importing a .env file into a vault and exporting secrets back out."""

from pathlib import Path

from envault.env_io import read_env_file, write_env_file, EnvParseError
from envault.vault import (
    VaultError,
    load_vault,
    save_vault,
    get_secret,
    set_secret,
)


def import_env(
    vault_path: Path,
    env_path: Path,
    passphrase: str,
    environment: str = "default",
    overwrite: bool = False,
) -> int:
    """Import all key/value pairs from a .env file into the vault.

    Returns the number of secrets imported.
    """
    try:
        secrets = read_env_file(env_path)
    except EnvParseError as exc:
        raise VaultError(f"Failed to parse env file: {exc}") from exc

    vault = load_vault(vault_path, passphrase)
    env_data = vault.setdefault("environments", {}).setdefault(environment, {})

    imported = 0
    for key, value in secrets.items():
        if key in env_data and not overwrite:
            continue
        env_data[key] = value
        imported += 1

    save_vault(vault_path, vault, passphrase)
    return imported


def export_env(
    vault_path: Path,
    env_path: Path,
    passphrase: str,
    environment: str = "default",
    overwrite: bool = False,
) -> int:
    """Export all secrets for an environment from the vault to a .env file.

    Returns the number of secrets exported.
    """
    if env_path.exists() and not overwrite:
        raise VaultError(
            f"{env_path} already exists. Use overwrite=True to replace it."
        )

    vault = load_vault(vault_path, passphrase)
    environments = vault.get("environments", {})

    if environment not in environments:
        raise VaultError(
            f"Environment {environment!r} not found in vault."
        )

    secrets = environments[environment]
    if not secrets:
        raise VaultError(f"No secrets found for environment {environment!r}.")

    write_env_file(env_path, secrets)
    return len(secrets)
