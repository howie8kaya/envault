import pytest
from pathlib import Path

from envault.vault import init_vault, set_secret, get_secret
from envault.commands.env_defaults import (
    apply_defaults,
    apply_defaults_from_file,
    list_defaults_candidates,
    DefaultsError,
)

PASS = "testpass"


@pytest.fixture
def vault_path(tmp_path):
    p = tmp_path / "vault.env"
    init_vault(p, PASS)
    return p


def test_apply_defaults_adds_missing_keys(vault_path):
    result = apply_defaults(vault_path, PASS, {"FOO": "bar", "BAZ": "qux"})
    assert "FOO" in result.applied
    assert "BAZ" in result.applied
    assert result.skipped == []


def test_applied_values_readable(vault_path):
    apply_defaults(vault_path, PASS, {"FOO": "bar"})
    assert get_secret(vault_path, PASS, "FOO") == "bar"


def test_existing_key_skipped_by_default(vault_path):
    set_secret(vault_path, PASS, "FOO", "original")
    result = apply_defaults(vault_path, PASS, {"FOO": "new"})
    assert "FOO" in result.skipped
    assert get_secret(vault_path, PASS, "FOO") == "original"


def test_existing_key_overwritten_when_flag_set(vault_path):
    set_secret(vault_path, PASS, "FOO", "original")
    result = apply_defaults(vault_path, PASS, {"FOO": "new"}, overwrite=True)
    assert "FOO" in result.applied
    assert get_secret(vault_path, PASS, "FOO") == "new"


def test_result_str_shows_applied_and_skipped(vault_path):
    set_secret(vault_path, PASS, "EXISTING", "val")
    result = apply_defaults(vault_path, PASS, {"EXISTING": "x", "NEW": "y"})
    s = str(result)
    assert "+ NEW" in s
    assert "~ EXISTING" in s


def test_result_str_empty_when_no_changes(vault_path):
    result = apply_defaults(vault_path, PASS, {})
    assert str(result) == "  (no changes)"


def test_apply_defaults_from_file(vault_path, tmp_path):
    env_file = tmp_path / ".env.defaults"
    env_file.write_text("DB_HOST=localhost\nDB_PORT=5432\n")
    result = apply_defaults_from_file(vault_path, PASS, env_file)
    assert "DB_HOST" in result.applied
    assert "DB_PORT" in result.applied
    assert get_secret(vault_path, PASS, "DB_HOST") == "localhost"


def test_apply_defaults_from_missing_file_raises(vault_path, tmp_path):
    with pytest.raises(DefaultsError, match="not found"):
        apply_defaults_from_file(vault_path, PASS, tmp_path / "missing.env")


def test_list_defaults_candidates(vault_path):
    set_secret(vault_path, PASS, "ALREADY", "here")
    candidates = list_defaults_candidates(vault_path, PASS, {"ALREADY": "x", "MISSING": "y"})
    assert candidates == ["MISSING"]
