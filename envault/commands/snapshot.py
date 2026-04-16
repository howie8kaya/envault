"""Snapshot management: save and restore vault states."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Optional

from envault.vault import load_vault, save_vault, VaultError

SNAPSHOT_DIR_NAME = ".envault_snapshots"


class SnapshotError(Exception):
    pass


def _snapshot_dir(vault_path: Path) -> Path:
    return vault_path.parent / SNAPSHOT_DIR_NAME


def create_snapshot(vault_path: Path, label: Optional[str] = None) -> Path:
    """Serialize current vault state to a timestamped snapshot file."""
    snap_dir = _snapshot_dir(vault_path)
    snap_dir.mkdir(exist_ok=True)

    raw = vault_path.read_text(encoding="utf-8")
    timestamp = int(time.time())
    slug = f"{timestamp}_{label}" if label else str(timestamp)
    snap_file = snap_dir / f"{slug}.json"

    meta = {"timestamp": timestamp, "label": label, "vault": json.loads(raw)}
    snap_file.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return snap_file


def list_snapshots(vault_path: Path) -> list[dict]:
    """Return snapshot metadata sorted newest-first."""
    snap_dir = _snapshot_dir(vault_path)
    if not snap_dir.exists():
        return []

    results = []
    for f in snap_dir.glob("*.json"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            results.append({"file": f, "timestamp": data["timestamp"], "label": data.get("label")})
        except (json.JSONDecodeError, KeyError):
            continue

    return sorted(results, key=lambda x: x["timestamp"], reverse=True)


def restore_snapshot(vault_path: Path, snapshot_file: Path) -> int:
    """Overwrite vault with data from a snapshot. Returns number of keys restored."""
    if not snapshot_file.exists():
        raise SnapshotError(f"Snapshot not found: {snapshot_file}")

    try:
        meta = json.loads(snapshot_file.read_text(encoding="utf-8"))
        vault_data = meta["vault"]
    except (json.JSONDecodeError, KeyError) as exc:
        raise SnapshotError(f"Corrupt snapshot file: {exc}") from exc

    vault_path.write_text(json.dumps(vault_data, indent=2), encoding="utf-8")
    return len(vault_data.get("secrets", {}))


def delete_snapshot(snapshot_file: Path) -> None:
    """Remove a snapshot file."""
    if not snapshot_file.exists():
        raise SnapshotError(f"Snapshot not found: {snapshot_file}")
    snapshot_file.unlink()


def find_snapshot(vault_path: Path, label: str) -> Optional[Path]:
    """Find the most recent snapshot matching the given label.

    Returns the snapshot file path, or None if no match is found.
    """
    for snap in list_snapshots(vault_path):
        if snap["label"] == label:
            return snap["file"]
    return None
