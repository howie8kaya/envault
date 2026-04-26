# env_audit_export

Export the audit log for a vault to JSON, CSV, or plain-text format.

## Overview

Every mutating operation recorded by the audit subsystem can be extracted and
shared with external tools (SIEM, spreadsheets, log aggregators) using
`export_audit`.

## API

### `export_audit(vault_path, fmt, keys, since) → AuditExportResult`

| Parameter    | Type              | Default  | Description                                      |
|--------------|-------------------|----------|--------------------------------------------------|
| `vault_path` | `Path`            | required | Path to the vault file.                          |
| `fmt`        | `str`             | `"json"` | Output format: `"json"`, `"csv"`, or `"text"`.   |
| `keys`       | `list[str] \| None` | `None`  | Restrict output to events matching these keys.   |
| `since`      | `str \| None`     | `None`   | ISO timestamp; skip events recorded before this. |

Raises `AuditExportError` if an unsupported format is requested.

### `AuditExportResult`

```python
@dataclass
class AuditExportResult:
    format: str        # the format used
    entry_count: int   # number of events in the output
    output: str        # the serialised content
```

`str(result)` → `"Exported 12 audit event(s) as json"`

## Examples

```python
from pathlib import Path
from envault.commands.env_audit_export import export_audit

result = export_audit(Path("prod.vault"), fmt="json")
print(result.output)
```

```python
# Only events for two specific keys, in CSV
result = export_audit(
    Path("prod.vault"),
    fmt="csv",
    keys=["DB_URL", "API_KEY"],
)
with open("audit.csv", "w") as f:
    f.write(result.output)
```

## Formats

### JSON
A JSON array of event objects, each matching the schema written by
`record_event`.

### CSV
Column headers are derived from the union of all keys present across all
events. Missing fields for a given row are left blank.

### Text
One line per event:
```
[2024-06-01T12:00:00] set key=DB_URL user=alice
[2024-06-01T12:01:00] rotate user=alice
```
If no events exist the output is `(no events)`.
