"""Tests for envault.commands.env_encode."""

from __future__ import annotations

import base64
import pytest

from envault.vault import init_vault, set_secret, get_secret
from envault.commands.env_encode import (
    EncodeError,
    encode_secrets,
    decode_secrets,
)


@pytest.fixture
def vault_path(tmp_path):
    p = tmp_path / "test.vault"
    init_vault(str(p), "pass")
    return str(p)


def test_encode_returns_result(vault_path):
    set_secret(vault_path, "pass", "API_KEY", "mysecret")
    result = encode_secrets(vault_path, "pass", keys=["API_KEY"])
    assert "API_KEY" in result.encoded


def test_encode_value_is_base64(vault_path):
    set_secret(vault_path, "pass", "TOKEN", "hello")
    encode_secrets(vault_path, "pass", keys=["TOKEN"])
    stored = get_secret(vault_path, "pass", "TOKEN")
    assert stored == base64.b64encode(b"hello").decode()


def test_encode_all_keys_when_none_specified(vault_path):
    set_secret(vault_path, "pass", "A", "foo")
    set_secret(vault_path, "pass", "B", "bar")
    result = encode_secrets(vault_path, "pass")
    assert set(result.encoded) == {"A", "B"}


def test_encode_missing_key_raises(vault_path):
    with pytest.raises(EncodeError, match="Key not found"):
        encode_secrets(vault_path, "pass", keys=["MISSING"])


def test_decode_restores_original_value(vault_path):
    original = "supersecret"
    set_secret(vault_path, "pass", "DB_PASS", original)
    encode_secrets(vault_path, "pass", keys=["DB_PASS"])
    decode_secrets(vault_path, "pass", keys=["DB_PASS"])
    restored = get_secret(vault_path, "pass", "DB_PASS")
    assert restored == original


def test_decode_returns_result(vault_path):
    set_secret(vault_path, "pass", "SECRET", base64.b64encode(b"data").decode())
    result = decode_secrets(vault_path, "pass", keys=["SECRET"])
    assert "SECRET" in result.decoded


def test_decode_invalid_base64_is_skipped(vault_path):
    set_secret(vault_path, "pass", "PLAIN", "not-base64!!!")
    result = decode_secrets(vault_path, "pass", keys=["PLAIN"])
    assert "PLAIN" in result.skipped
    assert "PLAIN" not in result.decoded


def test_decode_missing_key_raises(vault_path):
    with pytest.raises(EncodeError, match="Key not found"):
        decode_secrets(vault_path, "pass", keys=["GHOST"])


def test_encode_decode_str(vault_path):
    set_secret(vault_path, "pass", "X", "value")
    result = encode_secrets(vault_path, "pass", keys=["X"])
    assert "Encoded" in str(result)
    result2 = decode_secrets(vault_path, "pass", keys=["X"])
    assert "Decoded" in str(result2)


def test_encode_result_str_empty(vault_path):
    result_e = __import__(
        "envault.commands.env_encode", fromlist=["EncodeResult"]
    ).EncodeResult()
    assert str(result_e) == "Nothing to encode."
