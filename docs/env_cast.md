# env_cast — Type Casting for Vault Secrets

The `env_cast` module lets you retrieve vault secrets as typed Python values instead of raw strings.

## Supported Types

| Type    | Example input | Result          |
|---------|---------------|-----------------|
| `str`   | `"hello"`     | `"hello"`       |
| `int`   | `"42"`        | `42`            |
| `float` | `"3.14"`      | `3.14`          |
| `bool`  | `"true"`      | `True`          |
| `list`  | `"a, b, c"`   | `["a","b","c"]` |

### Bool truthy values
`1`, `true`, `yes`, `on` → `True`  
`0`, `false`, `no`, `off` → `False`

### List parsing
Comma-separated values are split and stripped.

## API

### `cast_secret(vault_path, passphrase, key, cast_type) -> CastResult`

Decrypts a single secret and casts it to the given type.

```python
from envault.commands.env_cast import cast_secret

result = cast_secret("prod.vault", "mypass", "MAX_RETRIES", "int")
print(result.value)  # 5
```

### `cast_all(vault_path, passphrase, type_map) -> list[CastResult]`

Cast multiple keys at once using a `{key: type}` mapping.

```python
results = cast_all("prod.vault", "mypass", {
    "PORT": "int",
    "DEBUG": "bool",
    "TAGS": "list",
})
```

## Errors

- `CastError` — raised when a key is missing, the type is unsupported, or the value cannot be converted.
