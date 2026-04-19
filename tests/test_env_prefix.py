import pytest
from pathlib import Path
from envault.vault import init_vault, set_secret, get_secret
from envault.commands.env_prefix import (
    add_prefix, strip_prefix, list_prefix_candidates, PrefixError
)

PASS = "testpass"


@pytest.fixture
def vault_path(tmp_path):
    p = tmp_path / "vault.env"
    init_vault(str(p), PASS)
    return str(p)


def test_add_prefix_renames_key(vault_path):
    set_secret(vault_path, PASS, "HOST", "localhost")
    result = add_prefix(vault_path, PASS, "APP_", keys=["HOST"])
    assert "APP_HOST" in result.affected


def test_add_prefix_value_readable(vault_path):
    set_secret(vault_path, PASS, "PORT", "5432")
    add_prefix(vault_path, PASS, "DB_", keys=["PORT"])
    assert get_secret(vault_path, PASS, "DB_PORT") == "5432"


def test_add_prefix_old_key_removed(vault_path):
    set_secret(vault_path, PASS, "NAME", "mydb")
    add_prefix(vault_path, PASS, "DB_", keys=["NAME"])
    with pytest.raises(Exception):
        get_secret(vault_path, PASS, "NAME")


def test_add_prefix_skips_existing_without_overwrite(vault_path):
    set_secret(vault_path, PASS, "KEY", "val1")
    set_secret(vault_path, PASS, "APP_KEY", "val2")
    result = add_prefix(vault_path, PASS, "APP_", keys=["KEY"])
    assert "KEY" in result.skipped


def test_add_prefix_missing_key_raises(vault_path):
    with pytest.raises(PrefixError):
        add_prefix(vault_path, PASS, "X_", keys=["GHOST"])


def test_add_prefix_empty_prefix_raises(vault_path):
    set_secret(vault_path, PASS, "A", "1")
    with pytest.raises(PrefixError):
        add_prefix(vault_path, PASS, "", keys=["A"])


def test_strip_prefix_renames_key(vault_path):
    set_secret(vault_path, PASS, "APP_HOST", "localhost")
    result = strip_prefix(vault_path, PASS, "APP_", keys=["APP_HOST"])
    assert "HOST" in result.affected


def test_strip_prefix_value_readable(vault_path):
    set_secret(vault_path, PASS, "APP_PORT", "8080")
    strip_prefix(vault_path, PASS, "APP_", keys=["APP_PORT"])
    assert get_secret(vault_path, PASS, "PORT") == "8080"


def test_strip_prefix_skips_non_matching(vault_path):
    set_secret(vault_path, PASS, "OTHER_KEY", "v")
    result = strip_prefix(vault_path, PASS, "APP_", keys=["OTHER_KEY"])
    assert "OTHER_KEY" in result.skipped


def test_strip_prefix_auto_selects_matching(vault_path):
    set_secret(vault_path, PASS, "APP_A", "1")
    set_secret(vault_path, PASS, "APP_B", "2")
    set_secret(vault_path, PASS, "OTHER", "3")
    result = strip_prefix(vault_path, PASS, "APP_")
    assert len(result.affected) == 2


def test_list_prefix_candidates(vault_path):
    set_secret(vault_path, PASS, "APP_X", "1")
    set_secret(vault_path, PASS, "APP_Y", "2")
    set_secret(vault_path, PASS, "OTHER", "3")
    candidates = list_prefix_candidates(vault_path, "APP_")
    assert set(candidates) == {"APP_X", "APP_Y"}
