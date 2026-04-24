# env_reorder

Reorder secrets within a vault either alphabetically or by providing an explicit key ordering.

## Functions

### `reorder_vault(vault_path, passphrase, key_order=None, alphabetical=False, reverse=False) -> ReorderResult`

Reorders the secrets stored in the vault.

**Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `vault_path` | `str` | Path to the vault file |
| `passphrase` | `str` | Vault passphrase |
| `key_order` | `list[str] \| None` | Explicit ordered list of keys |
| `alphabetical` | `bool` | Sort keys A–Z (or Z–A when `reverse=True`) |
| `reverse` | `bool` | Reverse the final ordering |

At least one of `key_order` or `alphabetical` must be provided, otherwise a `ReorderError` is raised.

When `key_order` is supplied but does not include every key, unlisted keys are appended in their original relative order.

### `current_order(vault_path, passphrase) -> list[str]`

Returns the current key ordering without modifying the vault.

## Return type — `ReorderResult`

```python
@dataclass
class ReorderResult:
    vault_path: str
    original_order: list[str]
    new_order: list[str]
    moved: int          # number of keys whose position changed
```

## Errors

- `ReorderError` — raised when no strategy is specified or when an unknown key is referenced in `key_order`.

## Examples

```python
from envault.commands.env_reorder import reorder_vault, current_order

# Sort alphabetically
result = reorder_vault("prod.vault", "s3cr3t", alphabetical=True)
print(result)  # Reordered 3 key(s) in 'prod.vault'

# Custom order
result = reorder_vault("prod.vault", "s3cr3t", key_order=["DB_URL", "API_KEY"])

# Inspect without changing
order = current_order("prod.vault", "s3cr3t")
print(order)  # ['DB_URL', 'API_KEY', 'SECRET']
```
