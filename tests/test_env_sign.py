"""Tests for envault.commands.env_sign."""

import pytest
from pathlib import Path

from envault.vault import init_vault, set_secret
from envault.commands.env_sign import (
    SignError,
    sign_vault,
    verify_vault,
)

PASS = "testpass"
SECRET_KEY = "my-signing-key"


@pytest.fixture
def vault_path(tmp_path):
    p = tmp_path / "test.vault"
    init_vault(p, PASS)
    set_secret(p, PASS, "API_KEY", "abc123")
    set_secret(p, PASS, "DB_URL", "postgres://localhost/db")
    return p


def test_sign_returns_result(vault_path):
    result = sign_vault(vault_path, PASS, SECRET_KEY)
    assert result.key_count == 2
    assert len(result.signature) == 64  # sha256 hex
    assert result.vault_path == vault_path


def test_sign_result_str(vault_path):
    result = sign_vault(vault_path, PASS, SECRET_KEY)
    s = str(result)
    assert "Signed 2 key(s)" in s
    assert "test.vault" in s


def test_sign_is_deterministic(vault_path):
    r1 = sign_vault(vault_path, PASS, SECRET_KEY)
    r2 = sign_vault(vault_path, PASS, SECRET_KEY)
    assert r1.signature == r2.signature


def test_sign_changes_with_different_key(vault_path):
    r1 = sign_vault(vault_path, PASS, SECRET_KEY)
    r2 = sign_vault(vault_path, PASS, "other-key")
    assert r1.signature != r2.signature


def test_verify_valid_signature(vault_path):
    result = sign_vault(vault_path, PASS, SECRET_KEY)
    verify = verify_vault(vault_path, PASS, SECRET_KEY, result.signature)
    assert verify.valid is True


def test_verify_invalid_signature(vault_path):
    verify = verify_vault(vault_path, PASS, SECRET_KEY, "a" * 64)
    assert verify.valid is False


def test_verify_result_str_valid(vault_path):
    result = sign_vault(vault_path, PASS, SECRET_KEY)
    verify = verify_vault(vault_path, PASS, SECRET_KEY, result.signature)
    assert "valid" in str(verify)
    assert "test.vault" in str(verify)


def test_verify_result_str_invalid(vault_path):
    verify = verify_vault(vault_path, PASS, SECRET_KEY, "bad" * 20 + "abcd")
    assert "INVALID" in str(verify)


def test_sign_missing_vault_raises(tmp_path):
    with pytest.raises(SignError, match="Vault not found"):
        sign_vault(tmp_path / "missing.vault", PASS, SECRET_KEY)


def test_sign_empty_secret_key_raises(vault_path):
    with pytest.raises(SignError, match="secret_key must not be empty"):
        sign_vault(vault_path, PASS, "")


def test_verify_missing_vault_raises(tmp_path):
    with pytest.raises(SignError, match="Vault not found"):
        verify_vault(tmp_path / "missing.vault", PASS, SECRET_KEY, "abc")


def test_sign_empty_vault(tmp_path):
    p = tmp_path / "empty.vault"
    init_vault(p, PASS)
    result = sign_vault(p, PASS, SECRET_KEY)
    assert result.key_count == 0
    assert len(result.signature) == 64
