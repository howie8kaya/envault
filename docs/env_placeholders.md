# Placeholder Detection

The `env_placeholders` module scans a vault for secrets that appear to be
unresolved placeholder values — values that were never filled in with real data.

## What Counts as a Placeholder?

The following patterns are flagged:

| Pattern | Example |
|---|---|
| Angle-bracket wrapped | `<your-api-key>`, `<fill-me-in>` |
| Mustache / double-brace | `{{SECRET}}`, `{{REPLACE_ME}}` |
| Literal `CHANGE_ME` | `CHANGE_ME` |
| Literal `TODO` | `TODO` |
| Literal `FIXME` | `FIXME` |

Matching is **case-insensitive** for keyword patterns.

## API

### `find_placeholders(vault_path, passphrase, keys=None) -> PlaceholderResult`

Scans the vault and returns a `PlaceholderResult`.

- `vault_path` — path to the `.vault` file
- `passphrase` — decryption passphrase
- `keys` — optional list of specific keys to check; raises `PlaceholderError` if any are missing

### `PlaceholderResult`

| Attribute | Type | Description |
|---|---|---|
| `total_keys` | `int` | Number of keys scanned |
| `count` | `int` | Number of placeholders found |
| `clean` | `bool` | `True` if no placeholders found |
| `entries` | `list[PlaceholderEntry]` | Detected placeholder entries |

### `PlaceholderEntry`

| Attribute | Type | Description |
|---|---|---|
| `key` | `str` | Secret key name |
| `value` | `str` | Decrypted value |
| `pattern_matched` | `str` | The matched placeholder text |

## Example

```python
from envault.commands.env_placeholders import find_placeholders

result = find_placeholders("prod.vault", "my-passphrase")

if not result.clean:
    print(result)
    for entry in result.entries:
        print(f"  Fix: {entry.key}")
```

## Errors

- `PlaceholderError` — raised when a specified key is not found in the vault.
