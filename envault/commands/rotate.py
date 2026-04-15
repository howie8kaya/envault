"""Key rotation support for envault vaults."""

from envault.vault import load_vault, save_vault, VaultError
from envault.crypto import encrypt, decrypt


def rotate_key(vault_path: str, old_passphrase: str, new_passphrase: str) -> int:
    """
    Re-encrypt all secrets in the vault with a new passphrase.

    Returns the number of secrets that were re-encrypted.
    Raises VaultError if the vault cannot be loaded or saved.
    Raises ValueError if the old passphrase is incorrect.
    """
    vault = load_vault(vault_path, old_passphrase)

    env = vault.get("env", "default")
    secrets: dict = vault.get("secrets", {})

    if not secrets:
        return 0

    # Decrypt all values with old passphrase, then re-encrypt with new one
    rotated: dict = {}
    for key, ciphertext in secrets.items():
        try:
            plaintext = decrypt(ciphertext, old_passphrase)
        except Exception as exc:
            raise VaultError(
                f"Failed to decrypt secret '{key}' during rotation: {exc}"
            ) from exc

        try:
            rotated[key] = encrypt(plaintext, new_passphrase)
        except Exception as exc:
            raise VaultError(
                f"Failed to re-encrypt secret '{key}' during rotation: {exc}"
            ) from exc

    vault["secrets"] = rotated
    save_vault(vault_path, vault, new_passphrase)

    return len(rotated)


def list_rotation_candidates(vault_path: str, passphrase: str) -> list[str]:
    """
    Return a sorted list of secret keys present in the vault.
    Useful for previewing what will be rotated.
    """
    vault = load_vault(vault_path, passphrase)
    secrets: dict = vault.get("secrets", {})
    return sorted(secrets.keys())
