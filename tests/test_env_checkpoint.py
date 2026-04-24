"""Tests for envault.commands.env_checkpoint."""

import time
import pytest
from pathlib import Path

from envault.vault import init_vault, set_secret
from envault.commands.env_checkpoint import (
    CheckpointError,
    CheckpointEntry,
    create_checkpoint,
    get_checkpoint,
    list_checkpoints,
    delete_checkpoint,
)

PASS = "test-pass"


@pytest.fixture
def vault_path(tmp_path):
    vp = tmp_path / "vault.env"
    init_vault(vp, PASS)
    set_secret(vp, PASS, "KEY_A", "alpha")
    set_secret(vp, PASS, "KEY_B", "beta")
    return vp


def test_create_checkpoint_returns_entry(vault_path):
    entry = create_checkpoint(vault_path, PASS, "v1")
    assert isinstance(entry, CheckpointEntry)
    assert entry.name == "v1"
    assert entry.key_count == 2


def test_create_checkpoint_stores_keys(vault_path):
    entry = create_checkpoint(vault_path, PASS, "snap")
    assert "KEY_A" in entry.keys
    assert "KEY_B" in entry.keys


def test_create_checkpoint_empty_name_raises(vault_path):
    with pytest.raises(CheckpointError, match="empty"):
        create_checkpoint(vault_path, PASS, "   ")


def test_get_checkpoint_returns_entry(vault_path):
    create_checkpoint(vault_path, PASS, "cp1")
    result = get_checkpoint(vault_path, "cp1")
    assert result is not None
    assert result.name == "cp1"
    assert result.key_count == 2


def test_get_checkpoint_returns_none_for_unknown(vault_path):
    assert get_checkpoint(vault_path, "nonexistent") is None


def test_list_checkpoints_empty_when_none(vault_path):
    assert list_checkpoints(vault_path) == []


def test_list_checkpoints_returns_all(vault_path):
    create_checkpoint(vault_path, PASS, "a")
    time.sleep(0.01)
    create_checkpoint(vault_path, PASS, "b")
    entries = list_checkpoints(vault_path)
    assert len(entries) == 2
    assert entries[0].name == "a"
    assert entries[1].name == "b"


def test_list_checkpoints_sorted_by_time(vault_path):
    create_checkpoint(vault_path, PASS, "first")
    time.sleep(0.01)
    create_checkpoint(vault_path, PASS, "second")
    entries = list_checkpoints(vault_path)
    assert entries[0].created_at <= entries[1].created_at


def test_delete_checkpoint_returns_true(vault_path):
    create_checkpoint(vault_path, PASS, "to_del")
    assert delete_checkpoint(vault_path, "to_del") is True


def test_delete_checkpoint_removes_entry(vault_path):
    create_checkpoint(vault_path, PASS, "gone")
    delete_checkpoint(vault_path, "gone")
    assert get_checkpoint(vault_path, "gone") is None


def test_delete_nonexistent_returns_false(vault_path):
    assert delete_checkpoint(vault_path, "nope") is False


def test_checkpoint_str_contains_name_and_keys(vault_path):
    entry = create_checkpoint(vault_path, PASS, "mycp")
    s = str(entry)
    assert "mycp" in s
    assert "KEY_A" in s
