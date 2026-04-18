# env_clone

Clone a vault into a new vault file, optionally filtering keys by prefix.

## Overview

`clone_vault` reads all (or a filtered subset of) secrets from a source vault and writes them into a freshly initialised destination vault, which can use a different passphrase.

This is useful for:
- Bootstrapping a new environment from an existing one.
- Splitting a large vault into smaller per-service vaults.
- Migrating to a new passphrase.

## API

### `clone_vault(src_path, dst_path, src_passphrase, dst_passphrase, prefix=None, overwrite=False) -> CloneResult`

| Parameter | Type | Description |
|---|---|---|
| `src_path` | `Path` | Source vault file. |
| `dst_path` | `Path` | Destination vault file (will be created). |
| `src_passphrase` | `str` | Passphrase for the source vault. |
| `dst_passphrase` | `str` | Passphrase for the destination vault. |
| `prefix` | `str \| None` | Only copy keys that start with this string. |
| `overwrite` | `bool` | Allow overwriting an existing destination vault. |

Raises `CloneError` if the source vault is missing or a key cannot be read.

### `list_clone_candidates(src_path, src_passphrase, prefix=None) -> List[str]`

Returns the sorted list of keys that *would* be copied given the supplied prefix filter, without performing the clone.

## CloneResult

```python
@dataclass
class CloneResult:
    source: Path
    destination: Path
    keys_copied: List[str]
    keys_skipped: List[str]
```

`str(result)` produces a human-readable summary, e.g.:

```
Cloned 4 key(s) from 'prod.vault' to 'staging.vault' (2 skipped).
```

## Example

```python
from pathlib import Path
from envault.commands.env_clone import clone_vault

result = clone_vault(
    src_path=Path("prod.vault"),
    dst_path=Path("staging.vault"),
    src_passphrase="prod-secret",
    dst_passphrase="staging-secret",
    prefix="APP_",
)
print(result)
```
