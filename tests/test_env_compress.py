"""Tests for envault.commands.env_compress."""
import pytest
from pathlib import Path

from envault.vault import init_vault, set_secret
from envault.commands.env_compress import (
    CompressError,
    CompressResult,
    compress_vault,
    decompress_into_vault,
)


@pytest.fixture
def vault_path(tmp_path):
    p = tmp_path / "test.vault"
    init_vault(p, "pass123")
    set_secret(p, "DB_URL", "postgres://localhost/db", "pass123")
    set_secret(p, "API_KEY", "supersecret", "pass123")
    set_secret(p, "PORT", "5432", "pass123")
    return p


def test_compress_returns_result(vault_path):
    result = compress_vault(vault_path, "pass123")
    assert isinstance(result, CompressResult)
    assert result.key_count == 3


def test_compress_payload_is_string(vault_path):
    result = compress_vault(vault_path, "pass123")
    assert isinstance(result.payload, str)
    assert len(result.payload) > 0


def test_compress_selective_keys(vault_path):
    result = compress_vault(vault_path, "pass123", keys=["DB_URL", "PORT"])
    assert result.key_count == 2


def test_compress_missing_key_raises(vault_path):
    with pytest.raises(CompressError, match="not found"):
        compress_vault(vault_path, "pass123", keys=["MISSING_KEY"])


def test_compress_wrong_passphrase_raises(vault_path):
    with pytest.raises(CompressError):
        compress_vault(vault_path, "wrongpass")


def test_compress_result_str(vault_path):
    result = compress_vault(vault_path, "pass123")
    s = str(result)
    assert "3 keys" in s
    assert "->" in s


def test_decompress_roundtrip(vault_path, tmp_path):
    result = compress_vault(vault_path, "pass123")
    dst = tmp_path / "dst.vault"
    imported = decompress_into_vault(result.payload, "pass123", dst)
    assert set(imported) == {"DB_URL", "API_KEY", "PORT"}


def test_decompress_values_correct(vault_path, tmp_path):
    result = compress_vault(vault_path, "pass123")
    dst = tmp_path / "dst.vault"
    decompress_into_vault(result.payload, "pass123", dst)
    from envault.vault import get_secret
    assert get_secret(dst, "DB_URL", "pass123") == "postgres://localhost/db"
    assert get_secret(dst, "API_KEY", "pass123") == "supersecret"


def test_decompress_skips_existing_without_overwrite(vault_path, tmp_path):
    result = compress_vault(vault_path, "pass123")
    dst = tmp_path / "dst.vault"
    decompress_into_vault(result.payload, "pass123", dst)
    imported = decompress_into_vault(result.payload, "pass123", dst, overwrite=False)
    assert imported == []


def test_decompress_overwrite_replaces_existing(vault_path, tmp_path):
    result = compress_vault(vault_path, "pass123")
    dst = tmp_path / "dst.vault"
    decompress_into_vault(result.payload, "pass123", dst)
    imported = decompress_into_vault(result.payload, "pass123", dst, overwrite=True)
    assert len(imported) == 3


def test_decompress_invalid_payload_raises(tmp_path):
    dst = tmp_path / "dst.vault"
    with pytest.raises(CompressError, match="Invalid payload"):
        decompress_into_vault("notvalidpayload!!", "pass123", dst)
