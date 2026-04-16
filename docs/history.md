# Key History

envault can track a lightweight history of value changes per key, storing previews (first 6 characters) so you can audit when a secret was rotated without storing plaintext.

## How It Works

History entries are stored inside the vault's `meta` block under `__history__`. Each entry records:
- **timestamp** — ISO 8601 UTC time of the change
- **value_preview** — first 6 characters of the value followed by `...`

Full plaintext values are **never** stored in history.

## API

### `record_history(vault_path, key, value, passphrase)`
Append a history entry for `key`. Call this after `set_secret`.

```python
from envault.commands.history import record_history
record_history("prod.vault", "API_KEY", new_value, passphrase)
```

### `get_history(vault_path, key, passphrase) -> List[HistoryEntry]`
Return all recorded entries for a key, oldest first.

```python
entries = get_history("prod.vault", "API_KEY", passphrase)
for e in entries:
    print(e)  # [2024-01-15T10:00:00+00:00] supers...
```

### `clear_history(vault_path, key, passphrase) -> int`
Remove all history for a key. Returns the number of entries deleted.

### `list_tracked_keys(vault_path, passphrase) -> List[str]`
Return all keys that have at least one history entry.

## Example Workflow

```python
from envault.vault import set_secret
from envault.commands.history import record_history, get_history

# After rotating a secret:
set_secret("prod.vault", "DB_PASS", new_password, passphrase)
record_history("prod.vault", "DB_PASS", new_password, passphrase)

# Audit later:
for entry in get_history("prod.vault", "DB_PASS", passphrase):
    print(entry)
```

## Notes

- History survives `rotate_key` since it lives in `meta` and is re-encrypted with the new passphrase.
- Use `clear_history` to prune old entries and keep vault size small.
