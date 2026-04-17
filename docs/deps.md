# Secret Dependencies

Track relationships between secrets — useful for understanding which secrets rely on others.

## Overview

Dependencies are stored as metadata inside the vault. They don't affect encryption or values — they're purely informational annotations.

## Usage

### Add a dependency

```python
from envault.commands.deps import add_dependency

info = add_dependency(vault_path, key="DB_POOL", depends_on="DB_URL", passphrase="...")
print(info)  # DB_POOL -> [DB_URL]
```

### Get dependencies for a key

```python
from envault.commands.deps import get_dependencies

info = get_dependencies(vault_path, key="DB_POOL", passphrase="...")
print(info.depends_on)  # ['DB_URL']
```

### Get dependents (reverse lookup)

```python
from envault.commands.deps import get_dependents

keys = get_dependents(vault_path, key="DB_URL", passphrase="...")
print(keys)  # ['DB_POOL', 'API_KEY']
```

### Remove a dependency

```python
from envault.commands.deps import remove_dependency

info = remove_dependency(vault_path, key="DB_POOL", depends_on="DB_URL", passphrase="...")
```

## Errors

- `DepsError` is raised if the key or dependency key doesn't exist in the vault.
- Removing a dependency that doesn't exist also raises `DepsError`.

## Notes

- Adding the same dependency twice is idempotent.
- Dependencies are not validated at decrypt time — they're advisory only.
