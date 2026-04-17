"""Tests for envault.commands.ttl."""
import time
import pytest
from pathlib import Path
from envault.vault import init_vault, set_secret
from envault.commands.ttl import set_ttl, get_ttl, purge_expired, TTLError

PASS = "hunter2"


@pytest.fixture
def vault_path(tmp_path):
    p = tmp_path / "test.vault"
    init_vault(p, PASS)
    set_secret(p, PASS, "API_KEY", "abc123")
    set_secret(p, PASS, "DB_PASS", "secret")
    return p


def test_set_ttl_returns_ttl_info(vault_path):
    info = set_ttl(vault_path, PASS, "API_KEY", 300)
    assert info.key == "API_KEY"
    assert info.remaining_seconds > 0
    assert not info.is_expired


def test_set_ttl_missing_key_raises(vault_path):
    with pytest.raises(TTLError, match="Key not found"):
        set_ttl(vault_path, PASS, "MISSING", 60)


def test_set_ttl_zero_seconds_raises(vault_path):
    with pytest.raises(TTLError, match="positive"):
        set_ttl(vault_path, PASS, "API_KEY", 0)


def test_get_ttl_returns_none_when_not_set(vault_path):
    assert get_ttl(vault_path, "API_KEY") is None


def test_get_ttl_returns_info_after_set(vault_path):
    set_ttl(vault_path, PASS, "API_KEY", 120)
    info = get_ttl(vault_path, "API_KEY")
    assert info is not None
    assert info.key == "API_KEY"
    assert info.remaining_seconds > 0


def test_ttl_info_str(vault_path):
    info = set_ttl(vault_path, PASS, "API_KEY", 60)
    s = str(info)
    assert "API_KEY" in s
    assert "expires at" in s


def test_purge_expired_removes_key(vault_path):
    set_ttl(vault_path, PASS, "API_KEY", 1)
    time.sleep(1.1)
    purged = purge_expired(vault_path, PASS)
    assert "API_KEY" in purged


def test_purge_expired_key_gone_from_vault(vault_path):
    from envault.vault import get_secret
    set_ttl(vault_path, PASS, "API_KEY", 1)
    time.sleep(1.1)
    purge_expired(vault_path, PASS)
    assert get_secret(vault_path, PASS, "API_KEY") is None


def test_purge_non_expired_key_kept(vault_path):
    from envault.vault import get_secret
    set_ttl(vault_path, PASS, "API_KEY", 300)
    purge_expired(vault_path, PASS)
    assert get_secret(vault_path, PASS, "API_KEY") == "abc123"


def test_purge_empty_vault_returns_empty(vault_path):
    result = purge_expired(vault_path, PASS)
    assert result == []
