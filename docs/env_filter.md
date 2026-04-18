# env_filter

Filter vault secrets by prefix, suffix, or glob pattern.

## Functions

### `filter_vault(vault_path, passphrase, *, prefix, suffix, pattern, invert) -> FilterResult`

Returns a `FilterResult` listing all keys that match the given criteria.

At least one of `prefix`, `suffix`, or `pattern` must be supplied. Multiple criteria are combined with OR logic. Set `invert=True` to return keys that do **not** match.

```python
result = filter_vault("prod.vault", "s3cr3t", prefix="DB_")
print(result)  # Matched 2/10 keys
print(result.matched)  # ['DB_HOST', 'DB_PORT']
```

### `extract_filtered(vault_path, passphrase, dest_path, dest_passphrase, **filter_kwargs) -> FilterResult`

Copies matched keys from the source vault into a destination vault, re-encrypting with the destination passphrase. The destination vault is created if it does not exist.

```python
extract_filtered(
    "prod.vault", "prod-pass",
    "db-only.vault", "new-pass",
    prefix="DB_",
)
```

## FilterResult

| Field | Type | Description |
|-------|------|-------------|
| `matched` | `list[str]` | Sorted list of matching key names |
| `total` | `int` | Total number of keys in the vault |

## Errors

- `FilterError` — raised when no filter criteria are provided.
