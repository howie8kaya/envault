# Secret Search

envault lets you search secrets stored in a vault by **key pattern** or **value substring**, without exposing sensitive data in plain text by default.

## Basic Usage

```bash
# Search keys containing "DB"
envault search DB --vault .env.vault

# Glob-style key matching
envault search "API_*" --vault .env.vault --glob

# Search inside decrypted values (masked output)
envault search localhost --vault .env.vault --search-values

# Reveal full values in output (use with care)
envault search DB --vault .env.vault --reveal
```

## Options

| Flag | Description |
|------|-------------|
| `--glob` | Treat pattern as a glob expression (e.g. `DB_*`) |
| `--search-values` | Also search inside decrypted secret values |
| `--reveal` | Print full decrypted values instead of masked output |
| `--case-sensitive` | Disable case-insensitive matching |
| `--vault PATH` | Path to the vault file (default: `.env.vault`) |

## Output Format

Each result line is prefixed with the match type:

```
[key]   DB_HOST=loca****
[value] API_KEY=abc1****
[both]  DB_PASSWORD=s3cr****
```

- `key` — the pattern matched the secret's key name
- `value` — the pattern matched the decrypted value
- `both` — both key and value matched

## Security Notes

- Values are **masked by default** — only the first 4 characters are shown.
- Use `--reveal` only in trusted environments; avoid piping output to logs.
- Searching values requires full decryption of every secret in the vault.
