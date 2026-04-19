import pytest
from pathlib import Path
from envault.vault import init_vault, set_secret, get_secret, load_vault
from envault.commands.env_trim import trim_vault, list_trim_candidates, TrimError


@pytest.fixture
def vault_path(tmp_path):
    p = tmp_path / "test.vault"
    init_vault(str(p), "pass")
    return str(p)


def test_trim_changes_whitespace_value(vault_path):
    data = load_vault(vault_path)
    set_secret(data, "KEY", "  hello  ", "pass")
    from envault.vault import save_vault
    save_vault(vault_path, data)

    result = trim_vault(vault_path, "pass")
    assert "KEY" in result.changed


def test_trim_value_is_clean_after_trim(vault_path):
    data = load_vault(vault_path)
    set_secret(data, "KEY", "  hello  ", "pass")
    from envault.vault import save_vault
    save_vault(vault_path, data)

    trim_vault(vault_path, "pass")
    data2 = load_vault(vault_path)
    assert get_secret(data2, "KEY", "pass") == "hello"


def test_trim_clean_value_is_skipped(vault_path):
    data = load_vault(vault_path)
    set_secret(data, "KEY", "clean", "pass")
    from envault.vault import save_vault
    save_vault(vault_path, data)

    result = trim_vault(vault_path, "pass")
    assert "KEY" in result.skipped
    assert "KEY" not in result.changed


def test_trim_selective_keys(vault_path):
    data = load_vault(vault_path)
    set_secret(data, "A", "  a  ", "pass")
    set_secret(data, "B", "  b  ", "pass")
    from envault.vault import save_vault
    save_vault(vault_path, data)

    result = trim_vault(vault_path, "pass", keys=["A"])
    assert "A" in result.changed
    assert "B" not in result.changed


def test_trim_missing_key_raises(vault_path):
    with pytest.raises(TrimError, match="not found"):
        trim_vault(vault_path, "pass", keys=["MISSING"])


def test_list_trim_candidates(vault_path):
    data = load_vault(vault_path)
    set_secret(data, "DIRTY", " value ", "pass")
    set_secret(data, "CLEAN", "value", "pass")
    from envault.vault import save_vault
    save_vault(vault_path, data)

    candidates = list_trim_candidates(vault_path, "pass")
    assert "DIRTY" in candidates
    assert "CLEAN" not in candidates


def test_trim_result_str_with_changes(vault_path):
    data = load_vault(vault_path)
    set_secret(data, "KEY", " v ", "pass")
    from envault.vault import save_vault
    save_vault(vault_path, data)

    result = trim_vault(vault_path, "pass")
    assert "Trimmed" in str(result)


def test_trim_result_str_no_changes(vault_path):
    data = load_vault(vault_path)
    set_secret(data, "KEY", "clean", "pass")
    from envault.vault import save_vault
    save_vault(vault_path, data)

    result = trim_vault(vault_path, "pass")
    assert "No keys" in str(result)
