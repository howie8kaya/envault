"""Tests for envault.commands.snapshot."""

from __future__ import annotations

import json
import time
import pytest
from pathlib import Path

from envault.vault import init_vault, set_secret
from envault.commands.snapshot import (
    SnapshotError,
    create_snapshot,
    list_snapshots,
    restore_snapshot,
    delete_snapshot,
    SNAPSHOT_DIR_NAME,
)

PASS = "hunter2"


@pytest.fixture
def vault_path(tmp_path) -> Path:
    vp = tmp_path / "test.vault"
    init_vault(vp, PASS)
    set_secret(vp, PASS, "KEY1", "val1")
    set_secret(vp, PASS, "KEY2", "val2")
    return vp


def test_create_snapshot_returns_path(vault_path):
    snap = create_snapshot(vault_path)
    assert snap.exists()
    assert snap.suffix == ".json"


def test_create_snapshot_with_label(vault_path):
    snap = create_snapshot(vault_path, label="before-deploy")
    assert "before-deploy" in snap.name


def test_create_snapshot_stores_vault_data(vault_path):
    snap = create_snapshot(vault_path)
    meta = json.loads(snap.read_text())
    assert "vault" in meta
    assert "timestamp" in meta
    assert isinstance(meta["timestamp"], int)


def test_list_snapshots_empty_when_none(vault_path):
    snaps = list_snapshots(vault_path)
    assert snaps == []


def test_list_snapshots_returns_all(vault_path):
    create_snapshot(vault_path, label="snap1")
    create_snapshot(vault_path, label="snap2")
    snaps = list_snapshots(vault_path)
    assert len(snaps) == 2


def test_list_snapshots_sorted_newest_first(vault_path):
    s1 = create_snapshot(vault_path, label="first")
    time.sleep(0.01)
    s2 = create_snapshot(vault_path, label="second")
    snaps = list_snapshots(vault_path)
    assert snaps[0]["label"] == "second"
    assert snaps[1]["label"] == "first"


def test_restore_snapshot_overwrites_vault(vault_path):
    snap = create_snapshot(vault_path, label="baseline")
    set_secret(vault_path, PASS, "KEY3", "val3")
    count = restore_snapshot(vault_path, snap)
    assert count == 2  # only KEY1 and KEY2 from snapshot


def test_restore_missing_snapshot_raises(vault_path, tmp_path):
    ghost = tmp_path / "ghost.json"
    with pytest.raises(SnapshotError, match="not found"):
        restore_snapshot(vault_path, ghost)


def test_restore_corrupt_snapshot_raises(vault_path, tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("{not valid json", encoding="utf-8")
    with pytest.raises(SnapshotError, match="Corrupt"):
        restore_snapshot(vault_path, bad)


def test_delete_snapshot_removes_file(vault_path):
    snap = create_snapshot(vault_path)
    delete_snapshot(snap)
    assert not snap.exists()


def test_delete_missing_snapshot_raises(vault_path, tmp_path):
    ghost = tmp_path / "nope.json"
    with pytest.raises(SnapshotError, match="not found"):
        delete_snapshot(ghost)
