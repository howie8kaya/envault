import pytest
from pathlib import Path
from envault.vault import init_vault, set_secret, load_vault
from envault.commands.compare import compare_vaults, format_compare, CompareEntry


@pytest.fixture
def left_vault(tmp_path):
    p = tmp_path / "left.vault"
    init_vault(str(p), "passL")
    v = load_vault(str(p))
    set_secret(v, "KEY_A", "alpha", "passL")
    set_secret(v, "SHARED", "same_val", "passL")
    set_secret(v, "DIFF", "left_val", "passL")
    from envault.vault import save_vault
    save_vault(str(p), v)
    return str(p)


@pytest.fixture
def right_vault(tmp_path):
    p = tmp_path / "right.vault"
    init_vault(str(p), "passR")
    v = load_vault(str(p))
    set_secret(v, "KEY_B", "beta", "passR")
    set_secret(v, "SHARED", "same_val", "passR")
    set_secret(v, "DIFF", "right_val", "passR")
    from envault.vault import save_vault
    save_vault(str(p), v)
    return str(p)


def test_left_only_key(left_vault, right_vault):
    results = compare_vaults(left_vault, "passL", right_vault, "passR")
    statuses = {e.key: e.status for e in results}
    assert statuses["KEY_A"] == "left_only"


def test_right_only_key(left_vault, right_vault):
    results = compare_vaults(left_vault, "passL", right_vault, "passR")
    statuses = {e.key: e.status for e in results}
    assert statuses["KEY_B"] == "right_only"


def test_changed_key(left_vault, right_vault):
    results = compare_vaults(left_vault, "passL", right_vault, "passR")
    statuses = {e.key: e.status for e in results}
    assert statuses["DIFF"] == "changed"


def test_same_key_excluded_by_default(left_vault, right_vault):
    results = compare_vaults(left_vault, "passL", right_vault, "passR")
    keys = [e.key for e in results]
    assert "SHARED" not in keys


def test_same_key_included_with_flag(left_vault, right_vault):
    results = compare_vaults(left_vault, "passL", right_vault, "passR", show_same=True)
    statuses = {e.key: e.status for e in results}
    assert statuses["SHARED"] == "same"


def test_format_compare_identical():
    assert format_compare([]) == "Vaults are identical."


def test_format_compare_shows_symbols(left_vault, right_vault):
    results = compare_vaults(left_vault, "passL", right_vault, "passR")
    output = format_compare(results)
    assert "<" in output or ">" in output or "~" in output


def test_compare_entry_str():
    e = CompareEntry(key="FOO", left_value="a", right_value="b")
    assert str(e).startswith("~")
