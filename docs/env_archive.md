# env_archive — Soft-Delete and Restore Secrets

The `env_archive` module lets you soft-delete secrets from an active vault without permanently losing their values. Archived secrets are hidden from normal operations but can be restored at any time, or permanently purged when no longer needed.

## Functions

### `archive_secret(vault_path, passphrase, key) -> ArchiveResult`

Moves `key` from the active secrets namespace into the archive. The secret is no longer accessible via `get_secret` but its value is preserved internally.

```python
result = archive_secret("vault.json", "my-pass", "OLD_API_KEY")
print(result)  # archived: OLD_API_KEY at 2024-06-01T12:00:00+00:00
```

Raises `ArchiveError` if the key does not exist.

### `restore_secret(vault_path, passphrase, key) -> ArchiveResult`

Moves `key` back from the archive into active secrets.

```python
result = restore_secret("vault.json", "my-pass", "OLD_API_KEY")
print(result)  # restored: OLD_API_KEY
```

Raises `ArchiveError` if the key is not currently archived, or if a live secret with the same name already exists.

### `list_archived(vault_path, passphrase) -> List[ArchiveResult]`

Returns all currently archived secrets with their archive timestamps.

```python
for entry in list_archived("vault.json", "my-pass"):
    print(entry.key, entry.archived_at)
```

### `purge_archived(vault_path, passphrase) -> List[str]`

Permanently deletes all archived secrets. Returns the list of purged keys.

```python
removed = purge_archived("vault.json", "my-pass")
print(f"Purged {len(removed)} archived secrets")
```

## ArchiveResult

| Field         | Type            | Description                              |
|---------------|-----------------|------------------------------------------|
| `key`         | `str`           | The secret key                           |
| `archived_at` | `str` or `None` | ISO-8601 UTC timestamp of archival       |
| `restored`    | `bool`          | `True` when the result represents a restore |

## Notes

- Archived secrets are stored under `__meta__.archived` inside the vault file and are encrypted at rest along with all other vault data.
- Archiving is not a substitute for key rotation — use `rotate_key` if you need to change the encryption passphrase.
