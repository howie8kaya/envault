# Vault Lock / Unlock

The `lock` module provides session-based passphrase caching so you don't need to re-enter your passphrase for every `envault` command.

## How It Works

When you unlock a vault, a session file is written to a temporary directory. The file stores the passphrase (protected by `chmod 600`) and an expiry timestamp. Subsequent commands can retrieve the cached passphrase automatically.

Session files are named based on a hash of the vault path, so multiple vaults can have independent sessions.

## API

### `unlock_vault(vault_path, passphrase, ttl=3600) -> str`

Verifies the passphrase against the vault and writes a session file. Returns the session token. Raises `VaultError` if the passphrase is incorrect.

### `lock_vault(vault_path) -> None`

Deletes the session file, requiring the passphrase to be entered again.

### `is_unlocked(vault_path) -> bool`

Returns `True` if a valid, non-expired session exists.

### `get_session_passphrase(vault_path) -> str | None`

Returns the cached passphrase if the session is valid, otherwise `None`. Automatically removes expired sessions.

### `session_info(vault_path) -> dict | None`

Returns metadata about the current session:

```python
{
    "expires_in": 3412,       # seconds remaining
    "token_prefix": "a3f9c1d2"  # first 8 chars of session token
}
```

Returns `None` if the vault is locked.

## Security Notes

- Session files are written to `$TMPDIR` (usually `/tmp`) with `600` permissions.
- The default TTL is **1 hour**. Pass a custom `ttl` (seconds) to `unlock_vault` to adjust.
- Passphrase is stored in plaintext within the session file — this is a convenience feature and relies on OS-level temp directory protections.
