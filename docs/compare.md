# Compare

The `compare` command lets you diff secrets between two vault files — useful when syncing environments or reviewing changes before a merge.

## Usage

```bash
envault compare left.vault right.vault
```

You will be prompted for each vault's passphrase separately.

## Output

Each key is prefixed with a symbol:

| Symbol | Meaning |
|--------|---------|
| `=`    | Same value in both vaults |
| `~`    | Key exists in both but values differ |
| `<`    | Key only in left vault |
| `>`    | Key only in right vault |

Example:

```
< DB_HOST   (only in left)
> REDIS_URL (only in right)
~ API_KEY   (values differ)
```

## Options

- `--show-same` — also display keys that are identical across both vaults
- `--left-pass` / `--right-pass` — supply passphrases non-interactively (use with care)

## Notes

- Decryption errors are shown as `<decrypt_error>` rather than crashing the comparison.
- Keys are sorted alphabetically in the output.
- This command is read-only and does not modify either vault.
