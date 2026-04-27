"""Tests for env_rollback command."""

import pytest

from envault.vault import init_vault, set_secret
from envault.commands.env_version import record_version
from envault.commands.env_rollback import (
    RollbackError,
    RollbackResult,
    rollback_secret,
    list_rollback_versions,
)


@pytest.fixture
def vault_path(tmp_path):
    p = tmp_path / "test.vault"
    init_vault(str(p), "pass")
    return str(p)


def _setup_versioned_key(vault_path, passphrase="pass"):
    set_secret(vault_path, passphrase, "API_KEY", "v1_secret")
    record_version(vault_path, passphrase, "API_KEY", note="initial")
    set_secret(vault_path, passphrase, "API_KEY", "v2_secret")
    record_version(vault_path, passphrase, "API_KEY", note="updated")
    set_secret(vault_path, passphrase, "API_KEY", "v3_secret")
    record_version(vault_path, passphrase, "API_KEY", note="latest")


def test_rollback_returns_result(vault_path):
    _setup_versioned_key(vault_path)
    result = rollback_secret(vault_path, "pass", "API_KEY", target_version=1)
    assert isinstance(result, RollbackResult)


def test_rollback_restores_old_value(vault_path):
    _setup_versioned_key(vault_path)
    rollback_secret(vault_path, "pass", "API_KEY", target_version=1)
    from envault.vault import get_secret
    val = get_secret(vault_path, "pass", "API_KEY")
    assert val == "v1_secret"


def test_rollback_result_str(vault_path):
    _setup_versioned_key(vault_path)
    result = rollback_secret(vault_path, "pass", "API_KEY", target_version=2)
    s = str(result)
    assert "API_KEY" in s
    assert "2" in s


def test_rollback_missing_key_raises(vault_path):
    with pytest.raises(RollbackError, match="not found"):
        rollback_secret(vault_path, "pass", "MISSING", target_version=1)


def test_rollback_no_history_raises(vault_path):
    set_secret(vault_path, "pass", "BARE_KEY", "somevalue")
    with pytest.raises(RollbackError, match="No version history"):
        rollback_secret(vault_path, "pass", "BARE_KEY", target_version=1)


def test_rollback_invalid_version_raises(vault_path):
    _setup_versioned_key(vault_path)
    with pytest.raises(RollbackError, match="Version 99 not found"):
        rollback_secret(vault_path, "pass", "API_KEY", target_version=99)


def test_list_rollback_versions_returns_list(vault_path):
    _setup_versioned_key(vault_path)
    versions = list_rollback_versions(vault_path, "pass", "API_KEY")
    assert len(versions) == 3


def test_list_rollback_versions_missing_key_raises(vault_path):
    with pytest.raises(RollbackError, match="not found"):
        list_rollback_versions(vault_path, "pass", "NO_SUCH_KEY")


def test_rollback_reverted_keys_populated(vault_path):
    _setup_versioned_key(vault_path)
    result = rollback_secret(vault_path, "pass", "API_KEY", target_version=1)
    assert "API_KEY" in result.reverted_keys
