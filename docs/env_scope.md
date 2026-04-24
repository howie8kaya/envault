# env_scope — Key Scope Management

Assign named **scopes** to vault keys to logically group them by domain or
service boundary (e.g. `backend`, `frontend`, `infra`, `auth`).

## Functions

### `set_scope(vault_path, passphrase, key, scope) -> ScopeInfo`

Assign `scope` to `key`.  The key must already exist in the vault.

```python
from envault.commands.env_scope import set_scope

info = set_scope("prod.vault", "s3cr3t", "DB_URL", "backend")
print(info)  # DB_URL -> scope:backend
```

### `get_scope(vault_path, passphrase, key) -> str | None`

Return the scope name for `key`, or `None` if no scope is assigned.

### `remove_scope(vault_path, passphrase, key) -> bool`

Remove the scope assignment for `key`.  Returns `True` if a scope was
removed, `False` if none was set.

### `list_by_scope(vault_path, passphrase, scope) -> ScopeResult`

Return a `ScopeResult` containing all keys that belong to `scope`.

```python
from envault.commands.env_scope import list_by_scope

result = list_by_scope("prod.vault", "s3cr3t", "backend")
print(result)  # scope:backend [2 key(s)]: CACHE_TTL, DB_URL
```

### `all_scopes(vault_path, passphrase) -> dict[str, list[str]]`

Return a mapping of every scope to its sorted list of keys.

```python
scopes = all_scopes("prod.vault", "s3cr3t")
# {"auth": ["API_KEY"], "backend": ["CACHE_TTL", "DB_URL"]}
```

## Data Classes

### `ScopeInfo`

| Field  | Type  | Description              |
|--------|-------|--------------------------|
| `key`  | `str` | The vault key            |
| `scope`| `str` | The assigned scope name  |

### `ScopeResult`

| Field  | Type        | Description                        |
|--------|-------------|------------------------------------|
| `scope`| `str`       | The queried scope name             |
| `keys` | `list[str]` | Sorted list of keys in that scope  |

## Errors

- `ScopeError` — raised when the target key does not exist or the scope
  name is blank.

## Notes

Scope metadata is stored under `__meta__.scopes` inside the vault file and
is never encrypted separately — it travels with the vault.
