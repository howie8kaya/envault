# Merge

The `merge` command combines secrets from one vault into another, giving you fine-grained control over conflicts.

## Usage

```python
from envault.commands.merge import merge_vaults, format_merge_results

results = merge_vaults(
    src_path="staging.vault",
    src_passphrase="staging-pass",
    dst_path="production.vault",
    dst_passphrase="prod-pass",
    overwrite=False,
)
print(format_merge_results(results))
```

## Parameters

| Parameter | Type | Description |
|---|---|---|
| `src_path` | `str` | Path to the source vault |
| `src_passphrase` | `str` | Passphrase for the source vault |
| `dst_path` | `str` | Path to the destination vault |
| `dst_passphrase` | `str` | Passphrase for the destination vault |
| `keys` | `list[str] \| None` | Specific keys to merge; all keys if omitted |
| `overwrite` | `bool` | Whether to overwrite existing keys (default: `False`) |

## Actions

Each key processed during a merge receives one of three actions:

- **added** — key did not exist in the destination and was inserted.
- **updated** — key existed in the destination and was overwritten (requires `overwrite=True`).
- **skipped** — key existed in the destination and `overwrite` was `False`.

## Output

`format_merge_results` returns a human-readable string:

```
+ API_KEY (added)
~ DB_URL (updated)
= REDIS_URL (skipped)

Summary: 1 added, 1 updated, 1 skipped.
```

## Errors

- `MergeError` — raised when a requested key does not exist in the source vault.
