# env_split — Split a Vault into Multiple Shards

The `env_split` module lets you divide a single vault into multiple smaller vaults, either by key prefix or by an explicit key mapping. This is useful when you want to distribute secrets across services or teams without sharing the entire vault.

---

## Functions

### `split_by_prefix(vault_path, passphrase, prefix_map, *, strip_prefix, overwrite) -> SplitResult`

Splits secrets into separate vaults based on key prefixes.

**Arguments:**

| Name | Type | Description |
|------|------|-------------|
| `vault_path` | `Path` | Source vault path |
| `passphrase` | `str` | Passphrase for source vault |
| `prefix_map` | `dict[str, Path]` | Mapping of prefix string to destination vault path |
| `strip_prefix` | `bool` | Remove the prefix from keys in destination vaults (default: `False`) |
| `overwrite` | `bool` | Overwrite existing destination vaults (default: `False`) |

**Returns:** `SplitResult`

---

### `split_by_map(vault_path, passphrase, key_map, dest_dir, *, overwrite) -> SplitResult`

Splits specific keys into named vault shards stored under `dest_dir`.

**Arguments:**

| Name | Type | Description |
|------|------|-------------|
| `vault_path` | `Path` | Source vault path |
| `passphrase` | `str` | Passphrase for source vault |
| `key_map` | `dict[str, list[str]]` | Mapping of shard label to list of keys |
| `dest_dir` | `Path` | Directory where `<label>.vault` files are created |
| `overwrite` | `bool` | Overwrite existing shard vaults (default: `False`) |

**Returns:** `SplitResult`

---

## SplitResult

```python
@dataclass
class SplitResult:
    source_path: Path
    shards: dict[str, Path]   # label/prefix -> vault path
    counts: dict[str, int]    # label/prefix -> number of keys written
```

**Example `str()` output:**

```
Split 'production.vault' into 2 shard(s):
  [DB_] db.vault — 2 key(s)
  [APP_] app.vault — 3 key(s)
```

---

## Errors

- `SplitError` — raised when a key listed in `key_map` does not exist in the source vault.

---

## Example

```python
from pathlib import Path
from envault.commands.env_split import split_by_prefix, split_by_map

# Split by prefix
result = split_by_prefix(
    Path("prod.vault"),
    "mypassphrase",
    {
        "DB_": Path("db.vault"),
        "APP_": Path("app.vault"),
    },
    strip_prefix=True,
)
print(result)

# Split by explicit key list
result = split_by_map(
    Path("prod.vault"),
    "mypassphrase",
    {"auth": ["JWT_SECRET", "OAUTH_KEY"]},
    dest_dir=Path("shards/"),
)
print(result)
```
