import pytest
from pathlib import Path
from envault.vault import init_vault, set_secret, get_secret, VaultError
from envault.commands.env_rename_bulk import (
    bulk_rename_by_prefix,
    bulk_rename_by_map,
    BulkRenameError,
)


@pytest.fixture
def vault_path(tmp_path):
    p = tmp_path / "test.vault"
    init_vault(str(p), "pass")
    return str(p)


def test_bulk_rename_by_prefix_renames_matching_keys(vault_path):
    set_secret(vault_path, "pass", "DEV_DB_HOST", "localhost")
    set_secret(vault_path, "pass", "DEV_DB_PORT", "5432")
    set_secret(vault_path, "pass", "PROD_DB_HOST", "prod.db")

    result = bulk_rename_by_prefix(vault_path, "pass", "DEV_", "STAGING_")
    assert ("DEV_DB_HOST", "STAGING_DB_HOST") in result.renamed
    assert ("DEV_DB_PORT", "STAGING_DB_PORT") in result.renamed
    assert len(result.renamed) == 2


def test_bulk_rename_by_prefix_old_keys_removed(vault_path):
    set_secret(vault_path, "pass", "DEV_API_KEY", "abc")
    bulk_rename_by_prefix(vault_path, "pass", "DEV_", "TEST_")
    with pytest.raises(VaultError):
        get_secret(vault_path, "pass", "DEV_API_KEY")


def test_bulk_rename_by_prefix_new_keys_readable(vault_path):
    set_secret(vault_path, "pass", "DEV_TOKEN", "secret123")
    bulk_rename_by_prefix(vault_path, "pass", "DEV_", "PROD_")
    assert get_secret(vault_path, "pass", "PROD_TOKEN") == "secret123"


def test_bulk_rename_by_prefix_skips_existing_without_overwrite(vault_path):
    set_secret(vault_path, "pass", "DEV_KEY", "old")
    set_secret(vault_path, "pass", "PROD_KEY", "existing")
    result = bulk_rename_by_prefix(vault_path, "pass", "DEV_", "PROD_")
    assert "DEV_KEY" in result.skipped
    assert get_secret(vault_path, "pass", "PROD_KEY") == "existing"


def test_bulk_rename_by_prefix_overwrite_replaces(vault_path):
    set_secret(vault_path, "pass", "DEV_KEY", "new_val")
    set_secret(vault_path, "pass", "PROD_KEY", "old_val")
    result = bulk_rename_by_prefix(vault_path, "pass", "DEV_", "PROD_", overwrite=True)
    assert ("DEV_KEY", "PROD_KEY") in result.renamed
    assert get_secret(vault_path, "pass", "PROD_KEY") == "new_val"


def test_bulk_rename_by_map_renames_keys(vault_path):
    set_secret(vault_path, "pass", "OLD_A", "val_a")
    set_secret(vault_path, "pass", "OLD_B", "val_b")
    result = bulk_rename_by_map(vault_path, "pass", {"OLD_A": "NEW_A", "OLD_B": "NEW_B"})
    assert ("OLD_A", "NEW_A") in result.renamed
    assert get_secret(vault_path, "pass", "NEW_A") == "val_a"
    assert get_secret(vault_path, "pass", "NEW_B") == "val_b"


def test_bulk_rename_by_map_missing_key_raises(vault_path):
    with pytest.raises(BulkRenameError, match="Key not found"):
        bulk_rename_by_map(vault_path, "pass", {"NONEXISTENT": "TARGET"})


def test_bulk_rename_result_str(vault_path):
    set_secret(vault_path, "pass", "A_KEY", "v")
    result = bulk_rename_by_prefix(vault_path, "pass", "A_", "B_")
    s = str(result)
    assert "A_KEY" in s
    assert "B_KEY" in s
