# env_redact

Redact vault secret values from arbitrary text or files.

Useful for sanitising log files, CI output, or config dumps before sharing.

## Functions

### `redact_text(text, vault_path, passphrase, placeholder="[REDACTED]", min_length=4)`

Scans `text` for occurrences of any decrypted vault secret and replaces them
with `placeholder`.

- Secrets shorter than `min_length` characters are skipped to avoid false
  positives on common short strings.
- Returns a `RedactResult`.

### `redact_file(file_path, vault_path, passphrase, placeholder="[REDACTED]", min_length=4, write=False)`

Reads a file and calls `redact_text` on its contents.

- If `write=True` the redacted content is written back to the same file.
- Raises `RedactError` on IO failure.

## RedactResult

| Field | Type | Description |
|-------|------|-------------|
| `original` | `str` | The input text before redaction |
| `redacted` | `str` | The text with secrets replaced |
| `replaced` | `list[str]` | Vault keys whose values were redacted |

```python
str(result)  # "Redacted 2 secret(s): API_KEY, DB_PASS"
```

## Example

```python
from envault.commands.env_redact import redact_text

result = redact_text(log_output, "prod.vault", passphrase)
print(result.redacted)
```
