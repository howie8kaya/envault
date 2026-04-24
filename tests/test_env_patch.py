"""Tests for envault/commands/env_patch.py"""

import pytest
from pathlib import Path

from envault.vault import init_vault, set_secret, get_secret
from envault.commands.env_patch import patch_vault, patch_vault_from_file, PatchError, PatchResult


PASS = "test-pass"


@pytest.fixture
def vault_path(tmp_path):
    p = tmp_path / "test.vault"
    init_vault(p, PASS)
    return p


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / "patch.env"
    f.write_text("NEW_KEY=hello\nANOTHER=world\n")
    return f


def test_patch_adds_new_keys(vault_path):
    result = patch_vault(vault_path, PASS, {"FOO": "bar", "BAZ": "qux"})
    assert "FOO" in result.applied
    assert "BAZ" in result.applied
    assert result.skipped == []


def test_patch_values_readable(vault_path):
    patch_vault(vault_path, PASS, {"MY_KEY": "my_value"})
    assert get_secret(vault_path, PASS, "MY_KEY") == "my_value"


def test_patch_skips_existing_by_default(vault_path):
    set_secret(vault_path, PASS, "EXISTING", "original")
    result = patch_vault(vault_path, PASS, {"EXISTING": "new_value"})
    assert "EXISTING" in result.skipped
    assert get_secret(vault_path, PASS, "EXISTING") == "original"


def test_patch_overwrites_when_flag_set(vault_path):
    set_secret(vault_path, PASS, "EXISTING", "original")
    result = patch_vault(vault_path, PASS, {"EXISTING": "updated"}, overwrite=True)
    assert "EXISTING" in result.overwritten
    assert get_secret(vault_path, PASS, "EXISTING") == "updated"


def test_patch_selective_keys(vault_path):
    result = patch_vault(vault_path, PASS, {"A": "1", "B": "2", "C": "3"}, keys=["A", "C"])
    assert "A" in result.applied
    assert "C" in result.applied
    assert "B" not in result.applied


def test_patch_selective_keys_unknown_raises(vault_path):
    with pytest.raises(PatchError, match="not present in patch source"):
        patch_vault(vault_path, PASS, {"A": "1"}, keys=["A", "MISSING"])


def test_patch_result_str_no_changes(vault_path):
    set_secret(vault_path, PASS, "KEY", "val")
    result = patch_vault(vault_path, PASS, {"KEY": "new"}, overwrite=False)
    assert str(result) == "No changes."


def test_patch_result_str_shows_summary(vault_path):
    set_secret(vault_path, PASS, "OLD", "v")
    result = patch_vault(vault_path, PASS, {"NEW": "x", "OLD": "y"}, overwrite=True)
    summary = str(result)
    assert "Added" in summary or "Updated" in summary


def test_patch_from_file_adds_keys(vault_path, env_file):
    result = patch_vault_from_file(vault_path, PASS, env_file)
    assert "NEW_KEY" in result.applied
    assert "ANOTHER" in result.applied


def test_patch_from_file_values_correct(vault_path, env_file):
    patch_vault_from_file(vault_path, PASS, env_file)
    assert get_secret(vault_path, PASS, "NEW_KEY") == "hello"
    assert get_secret(vault_path, PASS, "ANOTHER") == "world"


def test_patch_from_missing_file_raises(vault_path, tmp_path):
    with pytest.raises(PatchError, match="Failed to read env file"):
        patch_vault_from_file(vault_path, PASS, tmp_path / "nonexistent.env")


def test_patch_wrong_passphrase_raises(vault_path):
    with pytest.raises(PatchError, match="Failed to load vault"):
        patch_vault(vault_path, "wrong-pass", {"X": "y"})
