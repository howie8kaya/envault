# TTL — Time-to-Live for Secrets

The `ttl` module lets you attach an expiry duration to individual secrets. Once a secret's TTL elapses, it can be automatically purged from the vault.

## Functions

### `set_ttl(vault_path, passphrase, key, seconds) -> TTLInfo`

Attach a TTL to an existing secret. `seconds` must be a positive integer.

```python
from envault.commands.ttl import set_ttl

info = set_ttl(Path("prod.vault"), "mypass", "TEMP_TOKEN", 3600)
print(info)  # TEMP_TOKEN: expires at 2024-... (3600s remaining)
```

### `get_ttl(vault_path, key) -> TTLInfo | None`

Retrieve TTL information for a key. Returns `None` if no TTL is set.

```python
from envault.commands.ttl import get_ttl

info = get_ttl(Path("prod.vault"), "TEMP_TOKEN")
if info and info.is_expired:
    print("Token has expired!")
```

### `purge_expired(vault_path, passphrase) -> list[str]`

Scan the vault and permanently delete any secrets whose TTL has elapsed. Returns a list of the removed key names.

```python
from envault.commands.ttl import purge_expired

removed = purge_expired(Path("prod.vault"), "mypass")
print(f"Purged: {removed}")
```

## TTLInfo

| Field | Type | Description |
|---|---|---|
| `key` | str | Secret key name |
| `expires_at` | datetime | UTC expiry timestamp |
| `remaining_seconds` | float | Seconds until expiry (0 if expired) |
| `is_expired` | bool | True if TTL has elapsed |

## Storage

TTL metadata is stored alongside the vault file as `<vault>.ttl.json`. This file is unencrypted but contains no secret values — only key names and expiry timestamps.

> **Tip:** Run `purge_expired` as part of a cron job or startup hook to automatically clean up short-lived credentials.
