import pytest
from pathlib import Path

from envault.vault import init_vault, set_secret, get_secret
from envault.commands.env_archive import (
    ArchiveError,
    ArchiveResult,
    archive_secret,
    restore_secret,
    list_archived,
    purge_archived,
)

PASS = "test-pass"


@pytest.fixture
def vault_path(tmp_path):
    p = tmp_path / "vault.json"
    init_vault(str(p), PASS)
    set_secret(str(p), PASS, "DB_URL", "postgres://localhost/db")
    set_secret(str(p), PASS, "API_KEY", "secret-key-123")
    set_secret(str(p), PASS, "REDIS_URL", "redis://localhost")
    return str(p)


def test_archive_returns_result(vault_path):
    result = archive_secret(vault_path, PASS, "DB_URL")
    assert isinstance(result, ArchiveResult)
    assert result.key == "DB_URL"
    assert result.archived_at is not None
    assert result.restored is False


def test_archive_removes_from_active_secrets(vault_path):
    archive_secret(vault_path, PASS, "DB_URL")
    with pytest.raises(Exception):
        get_secret(vault_path, PASS, "DB_URL")


def test_archive_missing_key_raises(vault_path):
    with pytest.raises(ArchiveError, match="not found"):
        archive_secret(vault_path, PASS, "NONEXISTENT")


def test_archive_result_str(vault_path):
    result = archive_secret(vault_path, PASS, "API_KEY")
    s = str(result)
    assert "archived" in s
    assert "API_KEY" in s


def test_list_archived_empty_initially(vault_path):
    results = list_archived(vault_path, PASS)
    assert results == []


def test_list_archived_shows_archived_key(vault_path):
    archive_secret(vault_path, PASS, "DB_URL")
    results = list_archived(vault_path, PASS)
    keys = [r.key for r in results]
    assert "DB_URL" in keys


def test_list_archived_multiple(vault_path):
    archive_secret(vault_path, PASS, "DB_URL")
    archive_secret(vault_path, PASS, "API_KEY")
    results = list_archived(vault_path, PASS)
    assert len(results) == 2


def test_restore_returns_result(vault_path):
    archive_secret(vault_path, PASS, "DB_URL")
    result = restore_secret(vault_path, PASS, "DB_URL")
    assert isinstance(result, ArchiveResult)
    assert result.restored is True
    assert result.key == "DB_URL"


def test_restore_makes_secret_active_again(vault_path):
    archive_secret(vault_path, PASS, "DB_URL")
    restore_secret(vault_path, PASS, "DB_URL")
    val = get_secret(vault_path, PASS, "DB_URL")
    assert val == "postgres://localhost/db"


def test_restore_not_archived_raises(vault_path):
    with pytest.raises(ArchiveError, match="not archived"):
        restore_secret(vault_path, PASS, "DB_URL")


def test_restore_result_str(vault_path):
    archive_secret(vault_path, PASS, "REDIS_URL")
    result = restore_secret(vault_path, PASS, "REDIS_URL")
    assert "restored" in str(result)


def test_purge_archived_removes_all(vault_path):
    archive_secret(vault_path, PASS, "DB_URL")
    archive_secret(vault_path, PASS, "API_KEY")
    removed = purge_archived(vault_path, PASS)
    assert set(removed) == {"DB_URL", "API_KEY"}
    assert list_archived(vault_path, PASS) == []


def test_purge_empty_archive_returns_empty_list(vault_path):
    removed = purge_archived(vault_path, PASS)
    assert removed == []
