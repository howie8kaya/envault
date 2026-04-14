"""Tests for envault/vault.py"""

import json
import pytest
from pathlib import Path

from envault.vault import (
    init_vault,
    load_vault,
    save_vault,
    set_secret,
    get_secret,
    delete_secret,
    export_dotenv,
    VaultError,
)

PASSPHRASE = "super-secret-passphrase"


@pytest.fixture
def vault_path(tmp_path):
    return str(tmp_path / ".envault")


def test_init_vault_creates_file(vault_path):
    init_vault(vault_path, PASSPHRASE)
    assert Path(vault_path).exists()


def test_init_vault_raises_if_exists(vault_path):
    init_vault(vault_path, PASSPHRASE)
    with pytest.raises(VaultError, match="already exists"):
        init_vault(vault_path, PASSPHRASE)


def test_init_vault_overwrite(vault_path):
    init_vault(vault_path, PASSPHRASE)
    init_vault(vault_path, PASSPHRASE, overwrite=True)  # should not raise
    assert load_vault(vault_path, PASSPHRASE) == {}


def test_save_and_load_vault_roundtrip(vault_path):
    data = {"DB_HOST": "localhost", "DB_PORT": "5432"}
    save_vault(vault_path, PASSPHRASE, data)
    loaded = load_vault(vault_path, PASSPHRASE)
    assert loaded == data


def test_load_vault_wrong_passphrase(vault_path):
    save_vault(vault_path, PASSPHRASE, {"KEY": "value"})
    with pytest.raises(VaultError, match="Failed to decrypt"):
        load_vault(vault_path, "wrong-passphrase")


def test_load_vault_missing_file(vault_path):
    with pytest.raises(VaultError, match="not found"):
        load_vault(vault_path, PASSPHRASE)


def test_set_and_get_secret(vault_path):
    init_vault(vault_path, PASSPHRASE)
    set_secret(vault_path, PASSPHRASE, "API_KEY", "abc123")
    assert get_secret(vault_path, PASSPHRASE, "API_KEY") == "abc123"


def test_get_secret_missing_key(vault_path):
    init_vault(vault_path, PASSPHRASE)
    assert get_secret(vault_path, PASSPHRASE, "MISSING") is None


def test_delete_secret(vault_path):
    init_vault(vault_path, PASSPHRASE)
    set_secret(vault_path, PASSPHRASE, "TOKEN", "xyz")
    result = delete_secret(vault_path, PASSPHRASE, "TOKEN")
    assert result is True
    assert get_secret(vault_path, PASSPHRASE, "TOKEN") is None


def test_delete_secret_nonexistent(vault_path):
    init_vault(vault_path, PASSPHRASE)
    result = delete_secret(vault_path, PASSPHRASE, "NOPE")
    assert result is False


def test_export_dotenv(vault_path, tmp_path):
    init_vault(vault_path, PASSPHRASE)
    set_secret(vault_path, PASSPHRASE, "FOO", "bar")
    set_secret(vault_path, PASSPHRASE, "BAZ", "qux")
    output = str(tmp_path / ".env")
    export_dotenv(vault_path, PASSPHRASE, output)
    content = Path(output).read_text()
    assert "FOO=bar" in content
    assert "BAZ=qux" in content
