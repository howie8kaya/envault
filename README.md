# envault

A CLI tool for managing and encrypting `.env` files across multiple environments
with team-sharing support.

## Features

- AES-256 encrypted vault files
- Per-key history, expiry, TTL, and pin metadata
- Import / export `.env` files
- Diff, lint, search, and template rendering
- Snapshot & restore
- Team sharing via encrypted bundles
- Audit log for all mutations
- Key rotation with zero-downtime
- Environment profiles (`dev`, `staging`, `prod`)
- Copy / merge / clone vaults
- Bulk rename, prefix, uppercase, sort, squash, filter
- Schema validation and type checking
- Webhook notifications on vault events
- Secret generation with configurable charsets
- Dependency tracking between keys
- Group-based export
- Session-based vault locking / unlocking
- Backup & restore
- Alias resolution
- Notes and tags per key
- Access-control metadata per key
- Watch mode: sync a live `.env` file into the vault
- Template rendering with strict-mode
- Value interpolation (`${OTHER_KEY}` expansion)
- Cast secrets to typed values (int, float, bool, list)
- Redact secrets from arbitrary text or files
- Compress / decompress vault subsets
- Vault statistics
- Defaults manifest: seed missing keys from a file
- Trim whitespace from values
- Flatten nested JSON secrets into dot-notation keys
- Format / normalise key names
- **Vault chain resolution** — merge an ordered sequence of vaults with
  later-wins precedence (e.g. `base → staging → local`)

## Quick start

```bash
pip install envault

# create a new vault
envault init myapp.vault

# set a secret
envault set myapp.vault DATABASE_URL postgres://localhost/myapp

# export to .env
envault export myapp.vault > .env
```

## Vault chain example

```python
from pathlib import Path
from envault.commands.env_chain import resolve_chain

result = resolve_chain(
    vault_paths=[Path("base.vault"), Path("prod.vault")],
    passphrases=["base-pass", "prod-pass"],
)
print(result)
```

## Development

```bash
pip install -e .[dev]
pytest
```

## License

MIT
