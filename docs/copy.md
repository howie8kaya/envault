# Secret Copy

The `copy` command lets you copy secrets from one vault to another — useful when promoting secrets across environments (e.g. staging → production).

## Usage

```python
from envault.commands.copy import copy_secrets, list_copy_candidates

# Copy all secrets
copied = copy_secrets(
    src_path="staging.vault",
    src_passphrase="staging-pass",
    dst_path="prod.vault",
    dst_passphrase="prod-pass",
)
print(f"Copied: {copied}")

# Copy specific keys
copy_secrets(
    src_path="staging.vault",
    src_passphrase="staging-pass",
    dst_path="prod.vault",
    dst_passphrase="prod-pass",
    keys=["DB_URL", "API_KEY"],
    overwrite=True,
)
```

## Preview Before Copying

Use `list_copy_candidates` to see which keys are new vs already exist in the destination:

```python
candidates = list_copy_candidates("staging.vault", "prod.vault")
for key, status in candidates.items():
    print(f"{key}: {status}")
# DB_URL: new
# API_KEY: exists
```

## Behaviour

| Option | Default | Description |
|---|---|---|
| `keys` | `None` (all) | Specific keys to copy |
| `overwrite` | `False` | Overwrite existing keys in destination |

- Secrets are **re-encrypted** with the destination passphrase during copy.
- If any requested key is missing from the source, a `CopyError` is raised before any writes occur.
- Without `overwrite=True`, keys already present in the destination are silently skipped.
