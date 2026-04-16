"""Tests for envault.commands.expire."""

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from envault.commands.expire import (
    ExpireError,
    clear_expiry,
    get_expiry,
    list_expiring,
    set_expiry,
)
from envault.vault import init_vault, set_secret

PASS = "hunter2"


@pytest.fixture
def vault_path(tmp_path):
    p = tmp_path / "test.vault"
    init_vault(str(p), PASS)
    set_secret(str(p), PASS, "DB_URL", "postgres://localhost/db")
    set_secret(str(p), PASS, "API_KEY", "abc123")
    return str(p)


def test_set_expiry_returns_datetime(vault_path):
    result = set_expiry(vault_path, PASS, "DB_URL", 7)
    assert isinstance(result, datetime)
    assert result > datetime.now(timezone.utc)


def test_set_expiry_roughly_correct(vault_path):
    result = set_expiry(vault_path, PASS, "DB_URL", 10)
    expected = datetime.now(timezone.utc) + timedelta(days=10)
    assert abs((result - expected).total_seconds()) < 5


def test_set_expiry_missing_key_raises(vault_path):
    with pytest.raises(ExpireError, match="not found"):
        set_expiry(vault_path, PASS, "MISSING", 5)


def test_set_expiry_zero_days_raises(vault_path):
    with pytest.raises(ExpireError, match="positive"):
        set_expiry(vault_path, PASS, "DB_URL", 0)


def test_get_expiry_returns_info(vault_path):
    set_expiry(vault_path, PASS, "DB_URL", 5)
    info = get_expiry(vault_path, "DB_URL")
    assert info is not None
    assert info.key == "DB_URL"
    assert not info.expired


def test_get_expiry_none_when_not_set(vault_path):
    assert get_expiry(vault_path, "API_KEY") is None


def test_get_expiry_expired_flag(vault_path):
    set_expiry(vault_path, PASS, "API_KEY", 1)
    from envault.vault import load_vault, save_vault
    vault = load_vault(vault_path)
    past = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
    vault["meta"]["__expire_meta__"]["API_KEY"] = past
    save_vault(vault_path, vault)
    info = get_expiry(vault_path, "API_KEY")
    assert info.expired


def test_list_expiring_returns_soon_keys(vault_path):
    set_expiry(vault_path, PASS, "DB_URL", 5)
    set_expiry(vault_path, PASS, "API_KEY", 60)
    results = list_expiring(vault_path, within_days=30)
    keys = [r.key for r in results]
    assert "DB_URL" in keys
    assert "API_KEY" not in keys


def test_list_expiring_sorted(vault_path):
    set_expiry(vault_path, PASS, "API_KEY", 3)
    set_expiry(vault_path, PASS, "DB_URL", 1)
    results = list_expiring(vault_path, within_days=10)
    assert results[0].key == "DB_URL"


def test_clear_expiry_removes_entry(vault_path):
    set_expiry(vault_path, PASS, "DB_URL", 5)
    removed = clear_expiry(vault_path, "DB_URL")
    assert removed is True
    assert get_expiry(vault_path, "DB_URL") is None


def test_clear_expiry_not_set_returns_false(vault_path):
    assert clear_expiry(vault_path, "API_KEY") is False


def test_expiry_info_str(vault_path):
    set_expiry(vault_path, PASS, "DB_URL", 5)
    info = get_expiry(vault_path, "DB_URL")
    assert "DB_URL" in str(info)
    assert "ok" in str(info)
