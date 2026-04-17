# Backup & Restore

The `backup` module lets you export a vault to a portable bundle string and restore it later. Useful for quick off-site copies or handing a vault to a teammate without sharing the raw file.

## Creating a Backup

```python
from envault.commands.backup import create_backup

bundle = create_backup(vault_path)
# bundle is a JSON string — save it anywhere
with open("my_vault.bak", "w") as f:
    f.write(bundle)
```

The bundle contains:
- `version` — format version (currently `1`)
- `vault_name` — stem of the original vault file
- `created_at` — Unix timestamp of when the backup was made
- `data` — base64-encoded vault bytes

## Restoring a Backup

```python
from envault.commands.backup import restore_backup

with open("my_vault.bak") as f:
    bundle = f.read()

restore_backup(bundle, Path("restored.vault"))
```

Pass `overwrite=True` to replace an existing file at the destination.

## Inspecting a Bundle

```python
from envault.commands.backup import backup_info

info = backup_info(bundle)
print(info["vault_name"], info["created_at"])
```

`backup_info` returns metadata without writing anything to disk.

## Error Handling

All failures raise `BackupError` with a descriptive message:
- Vault file not found
- Invalid or unsupported bundle format
- Destination already exists (without `overwrite=True`)
