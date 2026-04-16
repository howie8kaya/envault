# Secret Pinning

Pinning a secret prevents it from being accidentally overwritten by `set_secret` or bulk import operations.

## Usage

```python
from envault.commands.pin import pin_secret, unpin_secret, is_pinned, list_pins

# Pin a secret
info = pin_secret("vault.env", "passphrase", "API_KEY")
print(info)  # API_KEY: pinned

# Check pin status
if is_pinned("vault.env", "passphrase", "API_KEY"):
    print("This key is protected")

# List all secrets with their pin status
for entry in list_pins("vault.env", "passphrase"):
    print(entry)

# Remove a pin
unpin_secret("vault.env", "passphrase", "API_KEY")
```

## API

### `pin_secret(vault_path, passphrase, key) -> PinInfo`
Marks the given key as pinned. Raises `PinError` if the key does not exist.

### `unpin_secret(vault_path, passphrase, key) -> PinInfo`
Removes the pin from a key. Safe to call even if the key is not pinned.

### `is_pinned(vault_path, passphrase, key) -> bool`
Returns `True` if the key is currently pinned.

### `list_pins(vault_path, passphrase) -> List[PinInfo]`
Returns a `PinInfo` entry for every secret in the vault.

## PinInfo

| Field   | Type  | Description                  |
|---------|-------|------------------------------|
| `key`   | `str` | The secret key name          |
| `pinned`| `bool`| Whether the key is pinned    |

## Notes

- Pin metadata is stored inside the vault under `__meta__.pins` and is encrypted along with the rest of the vault data.
- Pinning does not affect `rotate_key` — rotation re-encrypts all secrets regardless of pin status.
