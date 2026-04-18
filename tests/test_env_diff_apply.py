import pytest
from pathlib import Path
from envault.vault import init_vault, set_secret, get_secret
from envault.env_io import write_env_file, read_env_file
from envault.commands.env_diff_apply import apply_diff_to_vault, apply_diff_to_file

PASS = "testpass"


@pytest.fixture
def vault_path(tmp_path):
    p = tmp_path / "vault.env"
    init_vault(p, PASS)
    return p


@pytest.fixture
def env_file(tmp_path):
    return tmp_path / ".env"


def test_apply_diff_to_vault_adds_new_key(vault_path, env_file):
    write_env_file(env_file, {"NEW_KEY": "hello"})
    applied = apply_diff_to_vault(vault_path, env_file, PASS)
    assert any(e.key == "NEW_KEY" for e in applied)
    assert get_secret(vault_path, PASS, "NEW_KEY") == "hello"


def test_apply_diff_to_vault_skips_vault_only(vault_path, env_file):
    set_secret(vault_path, PASS, "VAULT_ONLY", "secret")
    write_env_file(env_file, {})
    applied = apply_diff_to_vault(vault_path, env_file, PASS)
    assert not applied


def test_apply_diff_to_vault_skips_changed_without_overwrite(vault_path, env_file):
    set_secret(vault_path, PASS, "KEY", "old")
    write_env_file(env_file, {"KEY": "new"})
    applied = apply_diff_to_vault(vault_path, env_file, PASS, overwrite=False)
    assert not applied
    assert get_secret(vault_path, PASS, "KEY") == "old"


def test_apply_diff_to_vault_overwrite_changed(vault_path, env_file):
    set_secret(vault_path, PASS, "KEY", "old")
    write_env_file(env_file, {"KEY": "new"})
    applied = apply_diff_to_vault(vault_path, env_file, PASS, overwrite=True)
    assert any(e.key == "KEY" for e in applied)
    assert get_secret(vault_path, PASS, "KEY") == "new"


def test_apply_diff_to_vault_selective_keys(vault_path, env_file):
    write_env_file(env_file, {"A": "1", "B": "2"})
    applied = apply_diff_to_vault(vault_path, env_file, PASS, keys=["A"])
    keys_applied = [e.key for e in applied]
    assert "A" in keys_applied
    assert "B" not in keys_applied


def test_apply_diff_to_file_exports_vault_key(vault_path, env_file):
    set_secret(vault_path, PASS, "EXPORTED", "val")
    applied = apply_diff_to_file(vault_path, env_file, PASS)
    assert any(e.key == "EXPORTED" for e in applied)
    result = read_env_file(env_file)
    assert result["EXPORTED"] == "val"


def test_apply_diff_to_file_skips_same(vault_path, env_file):
    set_secret(vault_path, PASS, "SAME", "val")
    write_env_file(env_file, {"SAME": "val"})
    applied = apply_diff_to_file(vault_path, env_file, PASS)
    assert not applied


def test_apply_diff_to_file_no_overwrite_changed(vault_path, env_file):
    set_secret(vault_path, PASS, "KEY", "vault_val")
    write_env_file(env_file, {"KEY": "file_val"})
    applied = apply_diff_to_file(vault_path, env_file, PASS, overwrite=False)
    assert not applied
    assert read_env_file(env_file)["KEY"] == "file_val"
