"""Tests for key rotation functionality."""

import pytest
from pathlib import Path

from envault.vault import init_vault, set_secret, get_secret, load_vault
from envault.commands.rotate import rotate_key, list_rotation_candidates


OLD_PASS = "old-super-secret"
NEW_PASS = "new-super-secret"


@pytest.fixture
def vault_path(tmp_path: Path) -> str:
    path = str(tmp_path / "test.vault")
    init_vault(path, OLD_PASS, env="staging")
    return path


def test_rotate_key_reencrypts_all_secrets(vault_path):
    set_secret(vault_path, OLD_PASS, "DB_URL", "postgres://localhost/db")
    set_secret(vault_path, OLD_PASS, "API_KEY", "abc123")

    count = rotate_key(vault_path, OLD_PASS, NEW_PASS)
    assert count == 2


def test_rotated_secrets_readable_with_new_passphrase(vault_path):
    set_secret(vault_path, OLD_PASS, "TOKEN", "my-token-value")

    rotate_key(vault_path, OLD_PASS, NEW_PASS)

    value = get_secret(vault_path, NEW_PASS, "TOKEN")
    assert value == "my-token-value"


def test_old_passphrase_fails_after_rotation(vault_path):
    set_secret(vault_path, OLD_PASS, "TOKEN", "secret")
    rotate_key(vault_path, OLD_PASS, NEW_PASS)

    from envault.vault import VaultError
    with pytest.raises((VaultError, Exception)):
        get_secret(vault_path, OLD_PASS, "TOKEN")


def test_rotate_empty_vault_returns_zero(vault_path):
    count = rotate_key(vault_path, OLD_PASS, NEW_PASS)
    assert count == 0


def test_rotate_wrong_old_passphrase_raises(vault_path):
    set_secret(vault_path, OLD_PASS, "KEY", "val")

    with pytest.raises(Exception):
        rotate_key(vault_path, "wrong-passphrase", NEW_PASS)


def test_list_rotation_candidates(vault_path):
    set_secret(vault_path, OLD_PASS, "ZEBRA", "z")
    set_secret(vault_path, OLD_PASS, "ALPHA", "a")
    set_secret(vault_path, OLD_PASS, "MANGO", "m")

    candidates = list_rotation_candidates(vault_path, OLD_PASS)
    assert candidates == ["ALPHA", "MANGO", "ZEBRA"]


def test_list_rotation_candidates_empty_vault(vault_path):
    candidates = list_rotation_candidates(vault_path, OLD_PASS)
    assert candidates == []


def test_rotate_preserves_all_secret_values(vault_path):
    """Ensure every secret value is intact after rotation, not just spot-checked."""
    secrets = {"DB_URL": "postgres://localhost/db", "API_KEY": "abc123", "TOKEN": "tok"}
    for key, value in secrets.items():
        set_secret(vault_path, OLD_PASS, key, value)

    rotate_key(vault_path, OLD_PASS, NEW_PASS)

    for key, expected in secrets.items():
        assert get_secret(vault_path, NEW_PASS, key) == expected
