# Secret Version Tracking

envault can record point-in-time snapshots of a secret's value, giving you a full version history and the ability to roll back to any previous value.

## Overview

| Function | Description |
|---|---|
| `record_version` | Snapshot the current value of a key |
| `get_versions` | List all recorded versions for a key |
| `rollback` | Restore a key to a previously recorded version |

## Usage

### Record a version

Call `record_version` before making a change you might want to undo:

```python
from envault.commands.env_version import record_version

entry = record_version("prod.vault", "passphrase", "API_KEY", note="pre-rotation")
print(entry)  # v1 [2024-05-01 12:00:00] (pre-rotation): 'abc12345...'
```

### List version history

```python
from envault.commands.env_version import get_versions

versions = get_versions("prod.vault", "passphrase", "API_KEY")
for v in versions:
    print(v)
```

### Roll back to a previous version

```python
from envault.commands.env_version import rollback

rollback("prod.vault", "passphrase", "API_KEY", version=1)
```

This overwrites the current live value with the snapshot from version 1.

## VersionEntry fields

- `version` — monotonically increasing integer (1-based)
- `value` — the plaintext secret value at the time of recording
- `recorded_at` — Unix timestamp of when the snapshot was taken
- `note` — optional free-text annotation

## Storage

Version history is stored inside the vault file under the `__meta__.versions` namespace, encrypted alongside all other vault data. No external files are created.

## Errors

- `VersionError` — raised when the key doesn't exist, has no history, or the requested version number is not found.
