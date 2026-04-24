"""Tests for envault.commands.env_reorder."""

import pytest

from envault.vault import init_vault, set_secret
from envault.commands.env_reorder import (
    ReorderError,
    ReorderResult,
    reorder_vault,
    current_order,
)


PASS = "testpass"


@pytest.fixture
def vault_path(tmp_path):
    p = tmp_path / "test.vault"
    init_vault(str(p), PASS)
    set_secret(str(p), PASS, "ZEBRA", "z")
    set_secret(str(p), PASS, "ALPHA", "a")
    set_secret(str(p), PASS, "MANGO", "m")
    return str(p)


def test_reorder_alphabetical(vault_path):
    result = reorder_vault(vault_path, PASS, alphabetical=True)
    assert result.new_order == ["ALPHA", "MANGO", "ZEBRA"]


def test_reorder_alphabetical_reverse(vault_path):
    result = reorder_vault(vault_path, PASS, alphabetical=True, reverse=True)
    assert result.new_order == ["ZEBRA", "MANGO", "ALPHA"]


def test_reorder_explicit_order(vault_path):
    result = reorder_vault(vault_path, PASS, key_order=["MANGO", "ZEBRA", "ALPHA"])
    assert result.new_order == ["MANGO", "ZEBRA", "ALPHA"]


def test_reorder_partial_order_appends_rest(vault_path):
    result = reorder_vault(vault_path, PASS, key_order=["MANGO"])
    assert result.new_order[0] == "MANGO"
    assert set(result.new_order) == {"ZEBRA", "ALPHA", "MANGO"}


def test_reorder_unknown_key_raises(vault_path):
    with pytest.raises(ReorderError, match="Unknown key"):
        reorder_vault(vault_path, PASS, key_order=["DOES_NOT_EXIST"])


def test_reorder_no_strategy_raises(vault_path):
    with pytest.raises(ReorderError):
        reorder_vault(vault_path, PASS)


def test_reorder_returns_result_type(vault_path):
    result = reorder_vault(vault_path, PASS, alphabetical=True)
    assert isinstance(result, ReorderResult)


def test_reorder_result_str(vault_path):
    result = reorder_vault(vault_path, PASS, alphabetical=True)
    s = str(result)
    assert "Reordered" in s
    assert "ALPHA" in s


def test_reorder_persists_to_vault(vault_path):
    reorder_vault(vault_path, PASS, alphabetical=True)
    order = current_order(vault_path, PASS)
    assert order == ["ALPHA", "MANGO", "ZEBRA"]


def test_current_order_returns_list(vault_path):
    order = current_order(vault_path, PASS)
    assert isinstance(order, list)
    assert len(order) == 3


def test_moved_count_correct(vault_path):
    # Original: ZEBRA, ALPHA, MANGO  ->  alphabetical: ALPHA, MANGO, ZEBRA
    result = reorder_vault(vault_path, PASS, alphabetical=True)
    assert result.moved > 0
