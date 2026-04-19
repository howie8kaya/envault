# env_prefix

Add or strip a prefix from secret keys in a vault.

## Functions

### `add_prefix(vault_path, passphrase, prefix, keys=None, overwrite=False) -> PrefixResult`

Adds `prefix` to each target key. If `keys` is `None`, all keys are targeted.
Returns a `PrefixResult` with `affected` and `skipped` lists.

```python
from envault.commands.env_prefix import add_prefix

result = add_prefix("prod.vault", "secret", "APP_")
print(result)
# Affected: 3, Skipped: 0
#   ~ APP_HOST
#   ~ APP_PORT
#   ~ APP_NAME
```

### `strip_prefix(vault_path, passphrase, prefix, keys=None, overwrite=False) -> PrefixResult`

Strips `prefix` from each target key. If `keys` is `None`, all keys starting with `prefix` are targeted.

```python
from envault.commands.env_prefix import strip_prefix

result = strip_prefix("prod.vault", "secret", "APP_")
```

### `list_prefix_candidates(vault_path, prefix) -> List[str]`

Returns all keys that start with `prefix`. Useful for previewing before stripping.

```python
from envault.commands.env_prefix import list_prefix_candidates

keys = list_prefix_candidates("prod.vault", "APP_")
# ["APP_HOST", "APP_PORT"]
```

## Errors

- `PrefixError` — raised when a target key is missing, the prefix is empty, or a naming conflict occurs (without `overwrite=True`).

## Notes

- When `overwrite=False` (default), keys that would conflict with an existing key are added to `skipped`.
- The original key is deleted after a successful rename.
