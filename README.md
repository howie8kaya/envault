# envault

A CLI tool for managing and encrypting `.env` files across multiple environments
with team-sharing support.

## Features

- **Encrypt / Decrypt** — AES-256-GCM encryption for all secrets
- **Import / Export** — Read and write `.env` files
- **Rotate** — Re-encrypt all secrets with a new passphrase
- **Share** — Export encrypted bundles for team members
- **Audit log** — Track every read and write event
- **Diff** — Compare vault contents against a `.env` file
- **Snapshots** — Save and restore point-in-time vault copies
- **Search** — Find secrets by key or value pattern
- **Lint** — Detect empty, placeholder, or duplicate values
- **Templates** — Render config files from vault secrets
- **Profiles** — Switch between named environment profiles
- **Copy** — Clone secrets between vaults
- **Rename** — Rename a secret key in place
- **Tags** — Label secrets with arbitrary tags
- **History** — Track value changes per key
- **Expiry** — Flag secrets that are past their rotation date
- **Pin** — Mark secrets as immutable
- **Watch** — Sync a live `.env` file into the vault on change
- **Notes** — Attach plaintext annotations to individual secrets

## Installation

```bash
pip install envault
```

## Quick Start

```python
from envault.vault import init_vault, set_secret, get_secret

init_vault("vault.json", "my-passphrase")
set_secret("vault.json", "my-passphrase", "API_KEY", "super-secret")
print(get_secret("vault.json", "my-passphrase", "API_KEY"))
```

## Modules

| Module | Purpose |
|--------|---------|
| `envault.crypto` | Low-level encrypt/decrypt primitives |
| `envault.vault` | Core vault read/write operations |
| `envault.env_io` | `.env` file parsing and serialisation |
| `envault.commands.*` | High-level feature commands |

## Development

```bash
pip install -e .[dev]
pytest
```
