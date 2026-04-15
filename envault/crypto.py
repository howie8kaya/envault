"""Encryption and decryption utilities for envault using AES-GCM."""

import os
import base64
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


NONCE_SIZE = 12  # bytes, standard for AES-GCM
KEY_SIZE = 32    # bytes, AES-256
SALT_SIZE = 16   # bytes


def derive_key(passphrase: str, salt: bytes) -> bytes:
    """Derive a 256-bit key from a passphrase using PBKDF2-HMAC-SHA256."""
    return hashlib.pbkdf2_hmac(
        "sha256",
        passphrase.encode("utf-8"),
        salt,
        iterations=600_000,
        dklen=KEY_SIZE,
    )


def encrypt(plaintext: str, passphrase: str) -> str:
    """Encrypt plaintext with a passphrase.

    Returns a base64-encoded string: salt(16) + nonce(12) + ciphertext.
    """
    salt = os.urandom(SALT_SIZE)
    nonce = os.urandom(NONCE_SIZE)
    key = derive_key(passphrase, salt)

    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)

    payload = salt + nonce + ciphertext
    return base64.b64encode(payload).decode("utf-8")


def decrypt(encoded: str, passphrase: str) -> str:
    """Decrypt a base64-encoded payload produced by encrypt().

    Raises ValueError on authentication failure or bad passphrase.
    """
    try:
        payload = base64.b64decode(encoded.encode("utf-8"))
    except Exception as exc:
        raise ValueError("Invalid encoded payload.") from exc

    min_length = SALT_SIZE + NONCE_SIZE + 1
    if len(payload) < min_length:
        raise ValueError(
            f"Payload too short: expected at least {min_length} bytes, got {len(payload)}."
        )

    salt = payload[:SALT_SIZE]
    nonce = payload[SALT_SIZE:SALT_SIZE + NONCE_SIZE]
    ciphertext = payload[SALT_SIZE + NONCE_SIZE:]

    key = derive_key(passphrase, salt)
    aesgcm = AESGCM(key)

    try:
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    except Exception as exc:
        raise ValueError("Decryption failed — wrong passphrase or corrupted data.") from exc

    return plaintext.decode("utf-8")
