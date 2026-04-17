"""Tests for envault.commands.lock."""

import time
from pathlib import Path

import pytest

from envault.commands.lock import (
    get_session_passphrase,
    is_unlocked,
    lock_vault,
    session_info,
    unlock_vault,
)
from envault.vault import VaultError, init_vault


@pytest.fixture
def vault_path(tmp_path):
    p = tmp_path / "test.vault"
    init_vault(p, "secret")
    return p


def test_unlock_returns_token(vault_path):
    token = unlock_vault(vault_path, "secret")
    assert isinstance(token, str) and len(token) == 64


def test_is_unlocked_after_unlock(vault_path):
    assert not is_unlocked(vault_path)
    unlock_vault(vault_path, "secret")
    assert is_unlocked(vault_path)


def test_lock_clears_session(vault_path):
    unlock_vault(vault_path, "secret")
    lock_vault(vault_path)
    assert not is_unlocked(vault_path)


def test_get_session_passphrase_returns_passphrase(vault_path):
    unlock_vault(vault_path, "secret")
    assert get_session_passphrase(vault_path) == "secret"


def test_get_session_passphrase_none_when_locked(vault_path):
    assert get_session_passphrase(vault_path) is None


def test_unlock_wrong_passphrase_raises(vault_path):
    with pytest.raises(VaultError):
        unlock_vault(vault_path, "wrong")


def test_session_expires(vault_path):
    unlock_vault(vault_path, "secret", ttl=1)
    time.sleep(1.1)
    assert get_session_passphrase(vault_path) is None


def test_session_info_returns_metadata(vault_path):
    unlock_vault(vault_path, "secret")
    info = session_info(vault_path)
    assert info is not None
    assert "expires_in" in info
    assert "token_prefix" in info
    assert len(info["token_prefix"]) == 8


def test_session_info_none_when_locked(vault_path):
    assert session_info(vault_path) is None


def test_lock_idempotent(vault_path):
    lock_vault(vault_path)  # no session exists, should not raise
    lock_vault(vault_path)
