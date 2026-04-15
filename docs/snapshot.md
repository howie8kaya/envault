# Vault Snapshots

The snapshot feature lets you capture and restore the full state of a vault file at any point in time. Snapshots are stored as plain JSON files in a `.envault_snapshots/` directory next to your vault.

## Creating a Snapshot

```python
from envault.commands.snapshot import create_snapshot
from pathlib import Path

snap_file = create_snapshot(Path("production.vault"), label="before-migration")
print(f"Snapshot saved to {snap_file}")
```

The optional `label` argument is embedded in the filename for easy identification.

## Listing Snapshots

```python
from envault.commands.snapshot import list_snapshots

for entry in list_snapshots(Path("production.vault")):
    print(entry["timestamp"], entry["label"], entry["file"])
```

Results are returned **newest-first**.

## Restoring a Snapshot

```python
from envault.commands.snapshot import restore_snapshot

count = restore_snapshot(Path("production.vault"), snap_file)
print(f"Restored {count} secrets")
```

> **Warning:** Restoring a snapshot **overwrites** the current vault file. Create a snapshot of the current state first if you need a rollback point.

## Deleting a Snapshot

```python
from envault.commands.snapshot import delete_snapshot

delete_snapshot(snap_file)
```

## Storage Layout

```
my-project/
  production.vault
  .envault_snapshots/
    1718000000_before-migration.json
    1717990000_initial.json
```

Each snapshot file contains:
- `timestamp` — Unix epoch of creation
- `label` — optional human-readable tag
- `vault` — full vault JSON payload (secrets remain encrypted)

## Security Note

Snapshot files contain the **encrypted** vault data, so they are safe to store alongside the vault. The encryption passphrase is never stored in snapshots.
