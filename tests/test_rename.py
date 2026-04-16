import pytest
from pathlib import Path
from envault.vault import init_vault, set_secret, get_secret
from envault.commands.rename import rename_secret, list_rename_candidates, RenameError


@pytest.fixture
def vault_path(tmp_path):
    p = tmp_path / "vault.env"
    init_vault(p, "pass123")
    set_secret(p, "pass123", "DB_HOST", "localhost")
    set_secret(p, "pass123", "DB_PORT", "5432")
    return p


def test_rename_changes_key(vault_path):
    rename_secret(vault_path, "DB_HOST", "DATABASE_HOST", "pass123")
    assert get_secret(vault_path, "pass123", "DATABASE_HOST") == "localhost"


def test_old_key_removed_after_rename(vault_path):
    rename_secret(vault_path, "DB_HOST", "DATABASE_HOST", "pass123")
    with pytest.raises(Exception):
        get_secret(vault_path, "pass123", "DB_HOST")


def test_rename_missing_key_raises(vault_path):
    with pytest.raises(RenameError, match="not found"):
        rename_secret(vault_path, "NONEXISTENT", "NEW_KEY", "pass123")


def test_rename_to_existing_key_raises(vault_path):
    with pytest.raises(RenameError, match="already exists"):
        rename_secret(vault_path, "DB_HOST", "DB_PORT", "pass123")


def test_rename_preserves_other_secrets(vault_path):
    rename_secret(vault_path, "DB_HOST", "DATABASE_HOST", "pass123")
    assert get_secret(vault_path, "pass123", "DB_PORT") == "5432"


def test_list_rename_candidates(vault_path):
    candidates = list_rename_candidates(vault_path, "pass123")
    assert "DB_HOST" in candidates
    assert "DB_PORT" in candidates


def test_rename_wrong_passphrase_raises(vault_path):
    with pytest.raises(Exception):
        rename_secret(vault_path, "DB_HOST", "DATABASE_HOST", "wrongpass")
