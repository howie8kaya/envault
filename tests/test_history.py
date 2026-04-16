import pytest
from pathlib import Path

from envault.vault import init_vault, set_secret
from envault.commands.history import (
    record_history,
    get_history,
    clear_history,
    list_tracked_keys,
)

PASS = "testpass"


@pytest.fixture
def vault_path(tmp_path):
    p = tmp_path / "test.vault"
    init_vault(str(p), PASS)
    set_secret(str(p), "API_KEY", "supersecret", PASS)
    set_secret(str(p), "DB_PASS", "hunter2", PASS)
    return str(p)


def test_record_and_get_history(vault_path):
    record_history(vault_path, "API_KEY", "supersecret", PASS)
    entries = get_history(vault_path, "API_KEY", PASS)
    assert len(entries) == 1
    assert entries[0].value_preview == "supers..."


def test_history_accumulates_entries(vault_path):
    record_history(vault_path, "API_KEY", "firstval", PASS)
    record_history(vault_path, "API_KEY", "secondval", PASS)
    entries = get_history(vault_path, "API_KEY", PASS)
    assert len(entries) == 2


def test_get_history_empty_for_unknown_key(vault_path):
    entries = get_history(vault_path, "NONEXISTENT", PASS)
    assert entries == []


def test_history_entry_str(vault_path):
    record_history(vault_path, "DB_PASS", "hunter2", PASS)
    entry = get_history(vault_path, "DB_PASS", PASS)[0]
    assert "hunter" in str(entry)
    assert "[" in str(entry)


def test_preview_short_value(vault_path):
    record_history(vault_path, "API_KEY", "abc", PASS)
    entry = get_history(vault_path, "API_KEY", PASS)[0]
    assert entry.value_preview == "abc"


def test_clear_history_returns_count(vault_path):
    record_history(vault_path, "API_KEY", "v1", PASS)
    record_history(vault_path, "API_KEY", "v2", PASS)
    count = clear_history(vault_path, "API_KEY", PASS)
    assert count == 2


def test_clear_history_removes_entries(vault_path):
    record_history(vault_path, "API_KEY", "v1", PASS)
    clear_history(vault_path, "API_KEY", PASS)
    assert get_history(vault_path, "API_KEY", PASS) == []


def test_list_tracked_keys(vault_path):
    record_history(vault_path, "API_KEY", "v1", PASS)
    record_history(vault_path, "DB_PASS", "v2", PASS)
    keys = list_tracked_keys(vault_path, PASS)
    assert set(keys) == {"API_KEY", "DB_PASS"}


def test_list_tracked_keys_empty(vault_path):
    assert list_tracked_keys(vault_path, PASS) == []
