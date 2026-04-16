"""Copy secrets between environments/vaults."""
from __future__ import annotations
from typing import Optional
from envault.vault import load_vault, save_vault, VaultError
from envault.crypto import decrypt, encrypt


class CopyError(Exception):
    pass


def copy_secrets(
    src_path: str,
    src_passphrase: str,
    dst_path: str,
    dst_passphrase: str,
    keys: Optional[list[str]] = None,
    overwrite: bool = False,
) -> list[str]:
    """Copy secrets from src vault to dst vault.

    Args:
        src_path: Path to source vault file.
        src_passphrase: Passphrase for source vault.
        dst_path: Path to destination vault file.
        dst_passphrase: Passphrase for destination vault.
        keys: List of keys to copy; if None, copy all.
        overwrite: Whether to overwrite existing keys in dst.

    Returns:
        List of keys that were copied.
    """
    src_vault = load_vault(src_path)
    dst_vault = load_vault(dst_path)

    src_secrets: dict = src_vault.get("secrets", {})
    dst_secrets: dict = dst_vault.get("secrets", {})

    keys_to_copy = keys if keys is not None else list(src_secrets.keys())

    missing = [k for k in keys_to_copy if k not in src_secrets]
    if missing:
        raise CopyError(f"Keys not found in source vault: {', '.join(missing)}")

    copied = []
    for key in keys_to_copy:
        if key in dst_secrets and not overwrite:
            continue
        plaintext = decrypt(src_secrets[key], src_passphrase)
        dst_secrets[key] = encrypt(plaintext, dst_passphrase)
        copied.append(key)

    dst_vault["secrets"] = dst_secrets
    save_vault(dst_path, dst_vault)
    return copied


def list_copy_candidates(src_path: str, dst_path: str) -> dict[str, str]:
    """Return keys showing overlap status between two vaults.

    Returns a dict mapping key -> 'new' | 'exists'.
    """
    src_vault = load_vault(src_path)
    dst_vault = load_vault(dst_path)
    src_keys = set(src_vault.get("secrets", {}).keys())
    dst_keys = set(dst_vault.get("secrets", {}).keys())
    return {k: ("exists" if k in dst_keys else "new") for k in src_keys}
