"""Tests for envault.crypto encryption/decryption."""

import pytest
from envault.crypto import encrypt, decrypt, derive_key


PASSPHRASE = "super-secret-passphrase"
PLAINTEXT = "DATABASE_URL=postgres://user:pass@localhost/mydb\nSECRET_KEY=abc123"


def test_encrypt_returns_string():
    result = encrypt(PLAINTEXT, PASSPHRASE)
    assert isinstance(result, str)
    assert len(result) > 0


def test_encrypt_produces_different_ciphertext_each_time():
    """Random salt/nonce means same input never produces same output."""
    result1 = encrypt(PLAINTEXT, PASSPHRASE)
    result2 = encrypt(PLAINTEXT, PASSPHRASE)
    assert result1 != result2


def test_decrypt_roundtrip():
    encoded = encrypt(PLAINTEXT, PASSPHRASE)
    recovered = decrypt(encoded, PASSPHRASE)
    assert recovered == PLAINTEXT


def test_decrypt_wrong_passphrase_raises():
    encoded = encrypt(PLAINTEXT, PASSPHRASE)
    with pytest.raises(ValueError, match="Decryption failed"):
        decrypt(encoded, "wrong-passphrase")


def test_decrypt_corrupted_payload_raises():
    encoded = encrypt(PLAINTEXT, PASSPHRASE)
    corrupted = encoded[:-4] + "AAAA"  # tamper with the end
    with pytest.raises(ValueError):
        decrypt(corrupted, PASSPHRASE)


def test_decrypt_invalid_base64_raises():
    with pytest.raises(ValueError, match="Invalid encoded payload"):
        decrypt("not-valid-base64!!!", PASSPHRASE)


def test_derive_key_length():
    import os
    salt = os.urandom(16)
    key = derive_key(PASSPHRASE, salt)
    assert len(key) == 32


def test_derive_key_deterministic():
    import os
    salt = os.urandom(16)
    key1 = derive_key(PASSPHRASE, salt)
    key2 = derive_key(PASSPHRASE, salt)
    assert key1 == key2


def test_encrypt_empty_string():
    encoded = encrypt("", PASSPHRASE)
    assert decrypt(encoded, PASSPHRASE) == ""
