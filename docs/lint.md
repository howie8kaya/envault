# `envault lint` — Secret Quality Checks

The `lint` command inspects your vault's secrets and reports common issues that could indicate security risks, misconfiguration, or poor hygiene.

## Usage

```bash
envault lint --vault <vault-file> --passphrase <passphrase>
```

## What It Checks

| Check | Severity | Description |
|---|---|---|
| Empty value | **error** | Secret exists but has no value |
| Decrypt failure | **error** | Could not decrypt — wrong passphrase or corrupted data |
| Placeholder value | **warning** | Value contains words like `changeme`, `todo`, `example` |
| Duplicate value | **warning** | Two or more keys share the exact same secret value |
| Short value | **warning** | Value is fewer than 8 characters |
| Generic key name | **info** | Key is named something overly broad like `SECRET` or `TOKEN` |

## Example Output

```
Found 3 issue(s) in 6 secret(s):

  ⚠ [WARNING] API_KEY: value looks like a placeholder (contains 'changeme')
  ⚠ [WARNING] DB_PASS: duplicate value shared with 'ADMIN_PASS'
  ℹ [INFO] SECRET: key name is very generic; consider a more descriptive name
```

When no issues are found:

```
✔ No issues found across 6 secret(s).
```

## Exit Codes

- `0` — no issues found
- `1` — one or more warnings or errors found

## Notes

- Linting requires the vault passphrase to decrypt values for inspection.
- Lint results are **not** recorded in the audit log by default.
- Use `envault diff` to compare vault contents against a live `.env` file.
