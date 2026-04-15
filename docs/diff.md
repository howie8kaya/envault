# Diff: Vault vs Local `.env` File

The `diff` command compares the secrets stored in a vault environment against a
local `.env` file. This is useful for spotting drift between what is committed
in the vault and what developers have locally.

## Usage

```python
from envault.commands.diff import diff_vault_vs_file, format_diff

entries = diff_vault_vs_file(
    vault_path=".envault",
    env_file_path=".env",
    passphrase="my-passphrase",
    env_name="default",       # optional, defaults to "default"
    show_unchanged=False,     # optional, hide identical keys
)

print(format_diff(entries))
```

## Output Symbols

| Symbol | Meaning |
|--------|---------|
| `+`    | Key exists only in the local file (not yet in vault) |
| `-`    | Key exists only in the vault (missing from local file) |
| `~`    | Key exists in both but values differ |
| ` `    | Key is identical in both (shown only with `show_unchanged=True`) |

## Example Output

```
+ NEW_KEY  (only in file)
- OLD_KEY  (only in vault)
~ DATABASE_URL  (vault != file)
```

## DiffEntry Fields

Each entry returned by `diff_vault_vs_file` is a `DiffEntry` dataclass:

- `key` — the environment variable name
- `status` — one of `added`, `removed`, `changed`, `unchanged`
- `vault_value` — decrypted value from the vault (`None` if not present)
- `file_value` — value from the local file (`None` if not present)

> **Note:** Values are decrypted in memory only and are never written to disk
> during a diff operation.
