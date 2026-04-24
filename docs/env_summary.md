# env_summary

Generate a human-readable summary report of a vault, showing key counts,
empty values, average secret length, and masked previews of each value.

## API

### `summarize_vault(vault_path, passphrase, keys=None) -> VaultSummary`

Decrypts and inspects every secret (or a subset) in the vault and returns
a `VaultSummary` object.

| Parameter | Type | Description |
|-----------|------|-------------|
| `vault_path` | `str` | Path to the `.vault` file |
| `passphrase` | `str` | Decryption passphrase |
| `keys` | `list[str] \| None` | Subset of keys to inspect; `None` = all |

Raises `SummaryError` if any requested key is not found in the vault.

---

### `VaultSummary`

| Field | Type | Description |
|-------|------|-------------|
| `vault_path` | `str` | Path of the inspected vault |
| `total_keys` | `int` | Number of keys inspected |
| `empty_keys` | `int` | Number of keys with empty values |
| `avg_length` | `float` | Average character length of all values |
| `entries` | `list[SummaryEntry]` | Per-key detail, sorted alphabetically |

Casting to `str` produces a formatted report:

```
Vault : /path/to/my.vault
Keys  : 3
Empty : 1
Avg   : 12.3 chars
-------------------------------------------------------
  API_KEY                        32 chars     preview=sk-l****
  DB_PASSWORD                    EMPTY
  SECRET_TOKEN                   16 chars     preview=tok-****
```

---

### `SummaryEntry`

| Field | Type | Description |
|-------|------|-------------|
| `key` | `str` | Secret key name |
| `length` | `int` | Character length of the decrypted value |
| `is_empty` | `bool` | `True` when the value is an empty string |
| `preview` | `str` | First 4 chars followed by `*` masking |

---

## Example

```python
from envault.commands.env_summary import summarize_vault

summary = summarize_vault("production.vault", "my-passphrase")
print(summary)
```

## Errors

- `SummaryError` — raised when one or more requested keys are absent from
  the vault.
