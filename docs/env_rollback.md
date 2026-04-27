# env_rollback

Rollback a vault secret to a previously recorded version.

## Overview

The `env_rollback` module allows you to revert a secret to any version that was
previously captured via `record_version`. This is useful when a bad value is
pushed and you need to quickly restore a known-good state.

> **Note:** Version history must be recorded explicitly using `record_version`
> from `envault.commands.env_version`. Secrets without recorded history cannot
> be rolled back.

## Functions

### `rollback_secret(vault_path, passphrase, key, target_version) -> RollbackResult`

Reverts `key` to the value stored at `target_version`.

| Argument         | Type  | Description                         |
|------------------|-------|-------------------------------------|
| `vault_path`     | `str` | Path to the `.vault` file           |
| `passphrase`     | `str` | Vault decryption passphrase         |
| `key`            | `str` | Secret key to roll back             |
| `target_version` | `int` | Version number to restore           |

Raises `RollbackError` if:
- The key does not exist in the vault
- No version history is recorded for the key
- The requested version number does not exist

### `list_rollback_versions(vault_path, passphrase, key) -> List[dict]`

Returns all recorded version entries for `key`. Each entry contains:
- `version` — integer version number
- `value` — the secret value at that version
- `timestamp` — ISO 8601 timestamp of when the version was recorded
- `note` — optional annotation string

## Example

```python
from envault.commands.env_rollback import rollback_secret, list_rollback_versions

versions = list_rollback_versions("prod.vault", "mypass", "DB_PASSWORD")
for v in versions:
    print(v["version"], v["timestamp"], v.get("note", ""))

result = rollback_secret("prod.vault", "mypass", "DB_PASSWORD", target_version=2)
print(result)
```

## Related

- [`env_version`](env_version.md) — record and inspect version history
- [`snapshot`](snapshot.md) — full vault snapshots
