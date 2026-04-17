# Access Control

envault supports simple role-based access control (RBAC) so you can restrict which secrets each role or team member is allowed to read.

Access rules are stored in a sidecar file next to the vault (e.g. `my.vault` → `my.access.json`). The vault itself remains encrypted; the access file only records which keys each role is permitted to see.

## API

### `set_access(vault_path, role, keys)`
Grant `role` access to the specified list of `keys`. Replaces any previous grant for that role. Raises `AccessError` if a key does not exist in the vault.

```python
from envault.commands.access import set_access
set_access(Path("prod.vault"), "backend", ["DB_URL", "REDIS_URL"])
```

### `get_access(vault_path, role) → list | None`
Return the list of keys the role can access, or `None` if no rules are defined for that role.

### `revoke_access(vault_path, role) → bool`
Remove all access rules for a role. Returns `True` if a rule existed, `False` otherwise.

### `list_roles(vault_path) → list[str]`
Return all role names that have access rules defined.

### `filter_by_role(vault_path, passphrase, role) → dict`
Decrypt the vault and return only the secrets the role is allowed to read. Raises `AccessError` if no rules are defined for the role.

```python
from envault.commands.access import filter_by_role
secrets = filter_by_role(Path("prod.vault"), "mypassphrase", "frontend")
print(secrets)  # {"API_KEY": "secret-api"}
```

## Notes

- Access rules are **not encrypted**; treat the `.access.json` file as non-sensitive metadata.
- Roles are arbitrary strings — use whatever naming convention suits your team (`dev`, `ops`, `ci`, etc.).
- Setting access for a role replaces the previous rule entirely; to add a single key, read the existing list first.
