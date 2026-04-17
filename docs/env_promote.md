# env_promote

Promote secrets from one environment vault to another (e.g., staging → production).

## Functions

### `promote_secrets(src_path, dst_path, src_passphrase, dst_passphrase, keys=None, overwrite=False) -> list[str]`

Copies secrets from the source vault to the destination vault.

- `keys`: optional list of specific keys to promote; defaults to all keys in source.
- `overwrite`: if `False` (default), keys already present in the destination are skipped.
- Returns the list of keys that were actually written.

**Raises** `PromoteError` if a requested key does not exist in the source vault.

### `list_promote_candidates(src_path, dst_path, src_passphrase, dst_passphrase) -> dict`

Returns a dict with two lists:

```json
{
  "new": ["DB_URL", "API_KEY"],
  "existing": ["SHARED"]
}
```

- `new`: keys only in the source (will be added on promote).
- `existing`: keys present in both vaults (skipped unless `overwrite=True`).

## Example

```python
from pathlib import Path
from envault.commands.env_promote import promote_secrets, list_promote_candidates

candidates = list_promote_candidates(
    Path("staging.vault"), Path("prod.vault"),
    "staging-pass", "prod-pass"
)
print("New keys:", candidates["new"])

promoted = promote_secrets(
    Path("staging.vault"), Path("prod.vault"),
    "staging-pass", "prod-pass",
    overwrite=False,
)
print(f"Promoted {len(promoted)} secrets")
```

## Notes

- Source and destination vaults may use different passphrases.
- Secrets are decrypted from source and re-encrypted for the destination.
- Use `overwrite=True` carefully in production environments.
