"""Sign and verify vault contents using an HMAC signature."""

import hashlib
import hmac
import json
from dataclasses import dataclass
from pathlib import Path

from envault.vault import VaultError, load_vault


class SignError(Exception):
    pass


@dataclass
class SignResult:
    vault_path: Path
    signature: str
    key_count: int

    def __str__(self) -> str:
        return f"Signed {self.key_count} key(s) from '{self.vault_path.name}' → {self.signature[:16]}..."


@dataclass
class VerifyResult:
    valid: bool
    vault_path: Path
    signature: str

    def __str__(self) -> str:
        status = "valid" if self.valid else "INVALID"
        return f"Signature {status} for '{self.vault_path.name}'"


def _compute_signature(secrets: dict, secret_key: str) -> str:
    """Compute a deterministic HMAC-SHA256 over sorted vault contents."""
    payload = json.dumps(secrets, sort_keys=True, separators=(",", ":")).encode()
    sig = hmac.new(secret_key.encode(), payload, hashlib.sha256)
    return sig.hexdigest()


def sign_vault(vault_path: Path, passphrase: str, secret_key: str) -> SignResult:
    """Generate an HMAC signature over all decrypted secrets in the vault."""
    if not vault_path.exists():
        raise SignError(f"Vault not found: {vault_path}")
    if not secret_key:
        raise SignError("secret_key must not be empty")

    try:
        vault = load_vault(vault_path, passphrase)
    except VaultError as exc:
        raise SignError(str(exc)) from exc

    secrets = vault.get("secrets", {})
    signature = _compute_signature(secrets, secret_key)
    return SignResult(vault_path=vault_path, signature=signature, key_count=len(secrets))


def verify_vault(vault_path: Path, passphrase: str, secret_key: str, expected: str) -> VerifyResult:
    """Verify that the vault signature matches the expected value."""
    if not vault_path.exists():
        raise SignError(f"Vault not found: {vault_path}")
    if not secret_key:
        raise SignError("secret_key must not be empty")

    try:
        vault = load_vault(vault_path, passphrase)
    except VaultError as exc:
        raise SignError(str(exc)) from exc

    secrets = vault.get("secrets", {})
    actual = _compute_signature(secrets, secret_key)
    valid = hmac.compare_digest(actual, expected)
    return VerifyResult(valid=valid, vault_path=vault_path, signature=actual)
