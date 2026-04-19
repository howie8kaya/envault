import pytest
import json
from pathlib import Path
from envault.vault import init_vault, set_secret, get_secret
from envault.commands.env_uppercase import uppercase_keys, list_uppercase_candidates, UppercaseError


@pytest.fixture
def vault_path(tmp_path):
    p = tmp_path / "test.vault"
    init_vault(str(p), "pass")
    return str(p)


def test_uppercase_renames_lowercase_key(vault_path):
    set_secret(vault_path, "db_host", "localhost", "pass")
    result = uppercase_keys(vault_path, "pass")
    assert any(old == "db_host" and new == "DB_HOST" for old, new in result.renamed)


def test_uppercased_value_readable(vault_path):
    set_secret(vault_path, "api_key", "secret123", "pass")
    uppercase_keys(vault_path, "pass")
    assert get_secret(vault_path, "API_KEY", "pass") == "secret123"


def test_already_uppercase_is_skipped(vault_path):
    set_secret(vault_path, "ALREADY", "val", "pass")
    result = uppercase_keys(vault_path, "pass")
    assert "ALREADY" in result.skipped
    assert not any(new == "ALREADY" for _, new in result.renamed)


def test_old_key_removed_after_uppercase(vault_path):
    set_secret(vault_path, "lower", "v", "pass")
    uppercase_keys(vault_path, "pass")
    from envault.vault import load_vault
    data = load_vault(vault_path)
    assert "lower" not in data["secrets"]
    assert "LOWER" in data["secrets"]


def test_selective_keys(vault_path):
    set_secret(vault_path, "foo", "1", "pass")
    set_secret(vault_path, "bar", "2", "pass")
    result = uppercase_keys(vault_path, "pass", keys=["foo"])
    assert any(old == "foo" for old, _ in result.renamed)
    assert not any(old == "bar" for old, _ in result.renamed)


def test_missing_key_raises(vault_path):
    with pytest.raises(UppercaseError, match="Key not found"):
        uppercase_keys(vault_path, "pass", keys=["nonexistent"])


def test_list_uppercase_candidates(vault_path):
    set_secret(vault_path, "mixed_Key", "v", "pass")
    set_secret(vault_path, "UPPER", "v", "pass")
    candidates = list_uppercase_candidates(vault_path)
    assert "mixed_Key" in candidates
    assert "UPPER" not in candidates


def test_result_str_shows_renames(vault_path):
    set_secret(vault_path, "mykey", "val", "pass")
    result = uppercase_keys(vault_path, "pass")
    out = str(result)
    assert "mykey" in out
    assert "MYKEY" in out
