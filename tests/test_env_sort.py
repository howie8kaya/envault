"""Tests for envault.commands.env_sort."""

import pytest
from pathlib import Path
from envault.vault import init_vault, set_secret, load_vault, list_secrets, get_secret
from envault.commands.env_sort import sort_vault, is_sorted, SortResult

PASS = "sortpass"


@pytest.fixture
def vault_path(tmp_path) -> str:
    p = tmp_path / "test.vault"
    init_vault(str(p), PASS)
    return str(p)


def _populate(vault_path, keys):
    vault = load_vault(vault_path)
    for k in keys:
        set_secret(vault, k, f"val_{k}", PASS)
    from envault.vault import save_vault
    save_vault(vault_path, vault)


def test_sort_returns_sort_result(vault_path):
    _populate(vault_path, ["ZEBRA", "APPLE", "MANGO"])
    result = sort_vault(vault_path, PASS)
    assert isinstance(result, SortResult)


def test_sort_orders_keys_alphabetically(vault_path):
    _populate(vault_path, ["ZEBRA", "APPLE", "MANGO"])
    result = sort_vault(vault_path, PASS)
    assert result.sorted_order == ["APPLE", "MANGO", "ZEBRA"]


def test_sort_result_str(vault_path):
    _populate(vault_path, ["B", "A"])
    result = sort_vault(vault_path, PASS)
    assert "reordered" in str(result)


def test_sort_already_sorted_str(vault_path):
    _populate(vault_path, ["A", "B", "C"])
    result = sort_vault(vault_path, PASS)
    assert "already sorted" in str(result)


def test_sort_reverse(vault_path):
    _populate(vault_path, ["APPLE", "MANGO", "ZEBRA"])
    result = sort_vault(vault_path, PASS, reverse=True)
    assert result.sorted_order == ["ZEBRA", "MANGO", "APPLE"]


def test_sort_values_preserved(vault_path):
    _populate(vault_path, ["Z_KEY", "A_KEY"])
    sort_vault(vault_path, PASS)
    vault = load_vault(vault_path)
    assert get_secret(vault, "Z_KEY", PASS) == "val_Z_KEY"
    assert get_secret(vault, "A_KEY", PASS) == "val_A_KEY"


def test_sort_group_by_prefix(vault_path):
    _populate(vault_path, ["DB_PORT", "APP_NAME", "DB_HOST", "APP_ENV"])
    result = sort_vault(vault_path, PASS, group_by_prefix=True)
    # APP_ keys before DB_ keys, sorted within group
    assert result.sorted_order == ["APP_ENV", "APP_NAME", "DB_HOST", "DB_PORT"]


def test_is_sorted_true_when_sorted(vault_path):
    _populate(vault_path, ["A", "B", "C"])
    assert is_sorted(vault_path, PASS) is True


def test_is_sorted_false_when_unsorted(vault_path):
    _populate(vault_path, ["C", "A", "B"])
    assert is_sorted(vault_path, PASS) is False


def test_sort_empty_vault(vault_path):
    result = sort_vault(vault_path, PASS)
    assert result.sorted_order == []
    assert "already sorted" in str(result)
