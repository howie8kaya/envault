"""Team sharing support: export encrypted vault bundles and import shared secrets."""

from __future__ import annotations

import json
import base64
from pathlib import Path
from typing import Optional

from envault.vault import load_vault, save_vault, VaultError
from envault.crypto import encrypt, decrypt


class ShareError(Exception):
    pass


def export_shared_bundle(
    vault_path: Path,
    passphrase: str,
    recipient_passphrase: str,
    keys: Optional[list[str]] = None,
) -> str:
    """Export selected (or all) secrets re-encrypted with a recipient passphrase.

    Returns a base64-encoded JSON bundle string safe to share over text channels.
    """
    vault = load_vault(vault_path, passphrase)
    secrets = vault.get("secrets", {})

    if keys is not None:
        missing = [k for k in keys if k not in secrets]
        if missing:
            raise ShareError(f"Keys not found in vault: {', '.join(missing)}")
        secrets = {k: secrets[k] for k in keys}

    if not secrets:
        raise ShareError("No secrets to export.")

    # Decrypt each value then re-encrypt with recipient passphrase
    bundle: dict[str, str] = {}
    for key, ciphertext in secrets.items():
        plaintext = decrypt(ciphertext, passphrase)
        bundle[key] = encrypt(plaintext, recipient_passphrase)

    payload = json.dumps({"version": 1, "secrets": bundle})
    return base64.b64encode(payload.encode()).decode()


def import_shared_bundle(
    vault_path: Path,
    passphrase: str,
    bundle: str,
    bundle_passphrase: str,
    overwrite: bool = False,
) -> int:
    """Import secrets from a shared bundle into the local vault.

    Returns the number of secrets imported.
    """
    try:
        payload = json.loads(base64.b64decode(bundle.encode()).decode())
    except Exception as exc:
        raise ShareError(f"Invalid bundle format: {exc}") from exc

    if payload.get("version") != 1:
        raise ShareError("Unsupported bundle version.")

    vault = load_vault(vault_path, passphrase)
    secrets = vault.setdefault("secrets", {})

    imported = 0
    for key, ciphertext in payload.get("secrets", {}).items():
        if key in secrets and not overwrite:
            continue
        plaintext = decrypt(ciphertext, bundle_passphrase)
        secrets[key] = encrypt(plaintext, passphrase)
        imported += 1

    save_vault(vault_path, vault, passphrase)
    return imported
