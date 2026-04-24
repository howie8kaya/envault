"""Integration-style tests: reorder interacts correctly with other vault ops."""

import pytest

from envault.vault import init_vault, set_secret, get_secret
from envault.commands.env_reorder import reorder_vault, current_order
from envault.commands.search import search_vault


PASS = "intpass"


@pytest.fixture
def vault_path(tmp_path):
    p = tmp_path / "integration.vault"
    init_vault(str(p), PASS)
    for key, val in [("DELTA", "d"), ("BETA", "b"), ("GAMMA", "g"), ("ALPHA", "a")]:
        set_secret(str(p), PASS, key, val)
    return str(p)


def test_values_intact_after_reorder(vault_path):
    reorder_vault(vault_path, PASS, alphabetical=True)
    assert get_secret(vault_path, PASS, "DELTA") == "d"
    assert get_secret(vault_path, PASS, "BETA") == "b"
    assert get_secret(vault_path, PASS, "GAMMA") == "g"
    assert get_secret(vault_path, PASS, "ALPHA") == "a"


def test_search_still_works_after_reorder(vault_path):
    reorder_vault(vault_path, PASS, alphabetical=True)
    results = search_vault(vault_path, PASS, "BETA")
    assert len(results) == 1
    assert results[0].key == "BETA"


def test_double_reorder_is_idempotent(vault_path):
    reorder_vault(vault_path, PASS, alphabetical=True)
    order_first = current_order(vault_path, PASS)
    reorder_vault(vault_path, PASS, alphabetical=True)
    order_second = current_order(vault_path, PASS)
    assert order_first == order_second


def test_reorder_then_add_new_key_appended(vault_path):
    reorder_vault(vault_path, PASS, alphabetical=True)
    set_secret(vault_path, PASS, "ZULU", "z")
    order = current_order(vault_path, PASS)
    assert order[-1] == "ZULU"


def test_explicit_order_then_alpha_gives_sorted(vault_path):
    reorder_vault(vault_path, PASS, key_order=["GAMMA", "DELTA", "BETA", "ALPHA"])
    reorder_vault(vault_path, PASS, alphabetical=True)
    assert current_order(vault_path, PASS) == ["ALPHA", "BETA", "DELTA", "GAMMA"]
