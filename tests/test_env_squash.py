import pytest
from pathlib import Path

from envault.vault import init_vault, set_secret, get_secret, VaultError
from envault.commands.env_squash import squash_vault, list_squash_candidates, SquashError


PASSPHRASE = "testpass"


@pytest.fixture
def vault_path(tmp_path):
    p = tmp_path / "test.vault"
    init_vault(str(p), PASSPHRASE)
    return str(p)


def test_squash_no_duplicates_returns_empty_removed(vault_path):
    set_secret(vault_path, "KEY_A", "alpha", PASSPHRASE)
    set_secret(vault_path, "KEY_B", "beta", PASSPHRASE)
    result = squash_vault(vault_path, PASSPHRASE)
    assert result.removed == []
    assert set(result.kept) == {"KEY_A", "KEY_B"}


def test_squash_removes_duplicate_key(vault_path):
    set_secret(vault_path, "KEY_A", "same", PASSPHRASE)
    set_secret(vault_path, "KEY_B", "same", PASSPHRASE)
    result = squash_vault(vault_path, PASSPHRASE)
    assert len(result.removed) == 1
    removed_key = result.removed[0][0]
    assert removed_key in ("KEY_A", "KEY_B")


def test_squash_duplicate_key_no_longer_in_vault(vault_path):
    set_secret(vault_path, "KEY_A", "dup", PASSPHRASE)
    set_secret(vault_path, "KEY_B", "dup", PASSPHRASE)
    result = squash_vault(vault_path, PASSPHRASE)
    removed_key = result.removed[0][0]
    with pytest.raises(VaultError):
        get_secret(vault_path, removed_key, PASSPHRASE)


def test_squash_kept_key_still_readable(vault_path):
    set_secret(vault_path, "KEY_A", "dup", PASSPHRASE)
    set_secret(vault_path, "KEY_B", "dup", PASSPHRASE)
    result = squash_vault(vault_path, PASSPHRASE)
    kept_key = result.kept[0]
    assert get_secret(vault_path, kept_key, PASSPHRASE) == "dup"


def test_squash_empty_vault_returns_empty_result(vault_path):
    result = squash_vault(vault_path, PASSPHRASE)
    assert result.removed == []
    assert result.kept == []


def test_dry_run_does_not_delete(vault_path):
    set_secret(vault_path, "KEY_A", "same", PASSPHRASE)
    set_secret(vault_path, "KEY_B", "same", PASSPHRASE)
    result = list_squash_candidates(vault_path, PASSPHRASE)
    assert len(result.removed) == 1
    # Both keys still exist
    assert get_secret(vault_path, "KEY_A", PASSPHRASE) == "same"
    assert get_secret(vault_path, "KEY_B", PASSPHRASE) == "same"


def test_squash_result_str_with_duplicates(vault_path):
    set_secret(vault_path, "KEY_A", "same", PASSPHRASE)
    set_secret(vault_path, "KEY_B", "same", PASSPHRASE)
    result = squash_vault(vault_path, PASSPHRASE)
    text = str(result)
    assert "duplicate" in text.lower()


def test_squash_result_str_no_duplicates(vault_path):
    set_secret(vault_path, "KEY_A", "unique", PASSPHRASE)
    result = squash_vault(vault_path, PASSPHRASE)
    assert "No duplicate" in str(result)
