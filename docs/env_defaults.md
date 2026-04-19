# env_defaults — Apply Default Values to a Vault

The `env_defaults` module lets you fill in missing vault keys from a dictionary
or a `.env` file, without touching keys that already have values.

## Functions

### `apply_defaults(vault_path, passphrase, defaults, overwrite=False)`

Apply a `dict[str, str]` of default key/value pairs to the vault.

- Keys **not** present in the vault are added.
- Keys **already** present are skipped (unless `overwrite=True`).

Returns a `DefaultsResult`.

### `apply_defaults_from_file(vault_path, passphrase, defaults_file, overwrite=False)`

Parse a `.env` file and apply its contents as defaults.

Raises `DefaultsError` if the file is missing or unparseable.

### `list_defaults_candidates(vault_path, passphrase, defaults)`

Return a list of keys from `defaults` that are **not** yet in the vault.
Useful for previewing what would be applied.

## DefaultsResult

| Field | Type | Description |
|-------|------|-------------|
| `applied` | `list[str]` | Keys that were written to the vault |
| `skipped` | `list[str]` | Keys that were already present and left unchanged |

`str(result)` produces a human-readable summary:

```
  + NEW_KEY (applied)
  ~ EXISTING_KEY (skipped, already set)
```

## Example

```python
from envault.commands.env_defaults import apply_defaults_from_file

result = apply_defaults_from_file(
    vault_path=Path(".vault.env"),
    passphrase="secret",
    defaults_file=Path(".env.defaults"),
)
print(result)
```
