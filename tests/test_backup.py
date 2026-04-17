"""Tests for envault.commands.backup."""
import json
import time
import pytest
from pathlib import Path

from envault.vault import init_vault, set_secret
from envault.commands.backup import (
    BackupError,
    create_backup,
    restore_backup,
    backup_info,
)

PASS = "testpass"


@pytest.fixture
def vault_path(tmp_path):
    p = tmp_path / "test.vault"
    init_vault(p, PASS)
    set_secret(p, PASS, "KEY", "value")
    return p


def test_create_backup_returns_string(vault_path):
    bundle = create_backup(vault_path)
    assert isinstance(bundle, str)
    parsed = json.loads(bundle)
    assert parsed["version"] == 1
    assert "data" in parsed


def test_create_backup_includes_vault_name(vault_path):
    bundle = create_backup(vault_path)
    info = json.loads(bundle)
    assert info["vault_name"] == vault_path.stem


def test_create_backup_missing_vault_raises(tmp_path):
    with pytest.raises(BackupError, match="Vault not found"):
        create_backup(tmp_path / "ghost.vault")


def test_restore_backup_creates_file(vault_path, tmp_path):
    bundle = create_backup(vault_path)
    dest = tmp_path / "restored.vault"
    result = restore_backup(bundle, dest)
    assert result == dest
    assert dest.exists()


def test_restore_backup_roundtrip(vault_path, tmp_path):
    from envault.vault import get_secret
    bundle = create_backup(vault_path)
    dest = tmp_path / "restored.vault"
    restore_backup(bundle, dest)
    assert get_secret(dest, PASS, "KEY") == "value"


def test_restore_backup_raises_if_exists(vault_path, tmp_path):
    bundle = create_backup(vault_path)
    dest = tmp_path / "existing.vault"
    dest.write_text("existing")
    with pytest.raises(BackupError, match="already exists"):
        restore_backup(bundle, dest)


def test_restore_backup_overwrite(vault_path, tmp_path):
    bundle = create_backup(vault_path)
    dest = tmp_path / "existing.vault"
    dest.write_text("old")
    restore_backup(bundle, dest, overwrite=True)
    assert dest.stat().st_size > 3


def test_restore_invalid_bundle_raises(tmp_path):
    with pytest.raises(BackupError, match="Invalid backup bundle"):
        restore_backup("not json", tmp_path / "x.vault")


def test_restore_wrong_version_raises(tmp_path):
    bundle = json.dumps({"version": 99, "data": "", "vault_name": "x"})
    with pytest.raises(BackupError, match="Unsupported backup version"):
        restore_backup(bundle, tmp_path / "x.vault")


def test_backup_info_returns_metadata(vault_path):
    bundle = create_backup(vault_path)
    info = backup_info(bundle)
    assert info["version"] == 1
    assert info["vault_name"] == vault_path.stem
    assert isinstance(info["created_at"], float)
