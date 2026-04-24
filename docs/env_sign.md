# env_sign — Vault Signing & Verification

The `env_sign` module lets you generate and verify an HMAC-SHA256 signature over all secrets stored in a vault. This is useful for detecting tampering or drift between environments.

## How it works

All decrypted secret key/value pairs are serialised as a deterministically sorted JSON string and signed with HMAC-SHA256 using a caller-supplied `secret_key`. The resulting hex digest can be stored, shared, or compared later.

## API

### `sign_vault(vault_path, passphrase, secret_key) → SignResult`

Decrypts the vault and computes an HMAC signature over its contents.

| Argument | Type | Description |
|---|---|---|
| `vault_path` | `Path` | Path to the `.vault` file |
| `passphrase` | `str` | Vault decryption passphrase |
| `secret_key` | `str` | HMAC signing key (keep this secret) |

Raises `SignError` if the vault is missing, the passphrase is wrong, or `secret_key` is empty.

**Returns** a `SignResult` with:
- `.signature` — 64-character hex HMAC-SHA256 digest
- `.key_count` — number of secrets signed
- `.vault_path` — path to the vault

### `verify_vault(vault_path, passphrase, secret_key, expected) → VerifyResult`

Verifies that the vault's current contents match a previously recorded signature.

| Argument | Type | Description |
|---|---|---|
| `expected` | `str` | Hex digest to compare against |

**Returns** a `VerifyResult` with:
- `.valid` — `True` if signatures match
- `.signature` — the freshly computed signature

## Example

```python
from pathlib import Path
from envault.commands.env_sign import sign_vault, verify_vault

vault = Path("production.vault")
sig = sign_vault(vault, passphrase="s3cr3t", secret_key="ci-key").signature
print(sig)  # store this in CI

result = verify_vault(vault, passphrase="s3cr3t", secret_key="ci-key", expected=sig)
assert result.valid, "Vault has been tampered with!"
```

## Notes

- The signature covers **decrypted** values, so any change to a secret — even re-encryption — will be detected if the plaintext differs.
- Use a strong, randomly generated `secret_key` and store it separately from the vault passphrase.
