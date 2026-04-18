# env_sort — Sort Vault Keys

The `env_sort` module provides utilities to sort secrets in a vault alphabetically by key. Sorting helps keep vaults tidy and makes diffs easier to read.

## Functions

### `sort_vault(vault_path, passphrase, *, group_by_prefix=False, reverse=False) -> SortResult`

Sorts all secrets in the vault by key name.

- **group_by_prefix** — When `True`, keys are grouped by their prefix (the part before the first `_`). Within each group keys are sorted alphabetically.
- **reverse** — Sort in descending (Z→A) order.

Returns a `SortResult` with:
- `original_order` — key list before sorting
- `sorted_order` — key list after sorting
- `group_by_prefix` — whether prefix grouping was applied

```python
from envault.commands.env_sort import sort_vault

result = sort_vault("prod.vault", "passphrase", group_by_prefix=True)
print(result)
# Vault 'prod.vault' reordered (12 keys)
```

### `is_sorted(vault_path, passphrase, *, group_by_prefix=False) -> bool`

Returns `True` if the vault keys are already in sorted order. Useful for CI checks.

```python
from envault.commands.env_sort import is_sorted

if not is_sorted("prod.vault", "passphrase"):
    print("Vault keys are not sorted!")
```

## Example: Prefix Grouping

Given keys `DB_PORT`, `APP_NAME`, `DB_HOST`, `APP_ENV`, prefix grouping produces:

```
APP_ENV
APP_NAME
DB_HOST
DB_PORT
```

## Notes

- Sorting is non-destructive — all secret values are preserved.
- The vault file is saved after sorting.
- An empty vault is always considered sorted.
