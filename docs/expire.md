# Secret Expiry / TTL

envault lets you attach an expiry date to any secret. This helps teams rotate credentials on schedule and catch stale values before they become a security risk.

## Setting an expiry

```python
from envault.commands.expire import set_expiry

expires_at = set_expiry("prod.vault", "passphrase", "API_KEY", days=30)
print(f"API_KEY expires at {expires_at}")
```

Expiry is stored as ISO-8601 UTC in the vault's metadata block under `__expire_meta__`. It does **not** affect the encrypted secret value itself.

## Checking a single key

```python
from envault.commands.expire import get_expiry

info = get_expiry("prod.vault", "API_KEY")
if info is None:
    print("No expiry set.")
elif info.expired:
    print(f"{info.key} has EXPIRED — rotate immediately!")
else:
    print(info)  # API_KEY: expires 2025-08-01T12:00:00+00:00 [ok]
```

## Listing expiring secrets

```python
from envault.commands.expire import list_expiring

for entry in list_expiring("prod.vault", within_days=14):
    print(entry)
```

Returns secrets expiring within the given window, sorted soonest first. Already-expired secrets are included and flagged.

## Clearing an expiry

```python
from envault.commands.expire import clear_expiry

clear_expiry("prod.vault", "API_KEY")
```

Returns `True` if an expiry was removed, `False` if none was set.

## ExpiryInfo fields

| Field | Type | Description |
|-------|------|-------------|
| `key` | str | Secret key name |
| `expires_at` | datetime | UTC expiry timestamp |
| `expired` | bool | True if past expiry |

## Errors

- `ExpireError` — raised when the key doesn't exist or `days` is not positive.
