# Secret Groups

Groups let you organize vault secrets under named logical categories, making it easier to manage large vaults.

## Overview

A group is a named collection of secret keys. Groups are stored as metadata inside the vault and do not affect encryption or secret values.

## API

### `add_to_group(vault_path, passphrase, group, key) -> GroupInfo`

Adds `key` to the named group. Creates the group if it doesn't exist. Raises `GroupError` if the key is not in the vault.

### `remove_from_group(vault_path, passphrase, group, key) -> GroupInfo`

Removes `key` from the group. Raises `GroupError` if the group or key membership doesn't exist.

### `list_groups(vault_path, passphrase) -> List[GroupInfo]`

Returns all defined groups and their members.

### `get_group(vault_path, passphrase, group) -> Optional[GroupInfo]`

Returns a `GroupInfo` for the named group, or `None` if it doesn't exist.

### `delete_group(vault_path, passphrase, group) -> bool`

Deletes the group entirely. Does not delete the underlying secrets.

## GroupInfo

```python
@dataclass
class GroupInfo:
    name: str
    keys: List[str]
```

`str(group_info)` → `[database] DB_HOST, DB_PORT`

## Example

```python
from envault.commands.group import add_to_group, list_groups

add_to_group("prod.vault", "pass", "database", "DB_HOST")
add_to_group("prod "database", "DB_PORT")

for g in list_groups("prod.vault", "pass"):
    print(g)
```

## Notes

- A key can belong to multiple groups.
- Deleting a group does not remove secrets from the vault.
- Groups are persisted in vault metadata and survive re-encryption.
