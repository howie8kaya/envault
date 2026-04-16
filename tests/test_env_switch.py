"""Tests for envault.commands.env_switch."""

import pytest
from pathlib import Path

from envault.vault import init_vault, set_secret
from envault.commands.env_switch import (
    save_profile,
    switch_profile,
    list_profiles,
    delete_profile,
    SwitchError,
)


PASS = "hunter2"


@pytest.fixture
def vault_path(tmp_path):
    p = tmp_path / "test.vault"
    init_vault(p, PASS)
    set_secret(p, PASS, "DB_HOST", "localhost")
    set_secret(p, PASS, "DB_PORT", "5432")
    return p


def test_save_profile_creates_profiles_file(vault_path):
    save_profile(vault_path, PASS, "dev")
    profiles_path = vault_path.parent / (vault_path.stem + ".profiles.json")
    assert profiles_path.exists()


def test_list_profiles_empty_when_none(vault_path):
    assert list_profiles(vault_path) == []


def test_list_profiles_returns_saved_names(vault_path):
    save_profile(vault_path, PASS, "dev")
    save_profile(vault_path, PASS, "prod")
    result = list_profiles(vault_path)
    assert result == ["dev", "prod"]


def test_switch_profile_restores_secrets(vault_path):
    save_profile(vault_path, PASS, "dev")
    # Change a secret after saving
    set_secret(vault_path, PASS, "DB_HOST", "prod-db.example.com")
    count = switch_profile(vault_path, PASS, "dev")
    assert count == 2


def test_switch_profile_values_match_snapshot(vault_path):
    from envault.vault import get_secret
    save_profile(vault_path, PASS, "snapshot")
    set_secret(vault_path, PASS, "DB_HOST", "changed")
    switch_profile(vault_path, PASS, "snapshot")
    assert get_secret(vault_path, PASS, "DB_HOST") == "localhost"


def test_switch_profile_missing_raises(vault_path):
    save_profile(vault_path, PASS, "dev")
    with pytest.raises(SwitchError, match="does not exist"):
        switch_profile(vault_path, PASS, "staging")


def test_switch_no_profiles_file_raises(vault_path):
    with pytest.raises(SwitchError, match="No profiles file"):
        switch_profile(vault_path, PASS, "dev")


def test_delete_profile_removes_entry(vault_path):
    save_profile(vault_path, PASS, "dev")
    save_profile(vault_path, PASS, "prod")
    result = delete_profile(vault_path, "dev")
    assert result is True
    assert list_profiles(vault_path) == ["prod"]


def test_delete_profile_nonexistent_returns_false(vault_path):
    save_profile(vault_path, PASS, "dev")
    assert delete_profile(vault_path, "ghost") is False


def test_delete_profile_no_file_returns_false(vault_path):
    assert delete_profile(vault_path, "dev") is False
