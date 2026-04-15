# Audit Log

envault maintains an append-only audit log alongside each vault file.
The log is stored as newline-delimited JSON in `.envault_audit.log` in
the same directory as the vault.

## Event fields

| Field | Description |
|-------|-------------|
| `timestamp` | ISO-8601 UTC timestamp of the event |
| `action` | Operation performed (e.g. `set`, `get`, `rotate`, `export`) |
| `key` | Affected secret key, or `null` for vault-level operations |
| `actor` | Username taken from `$USER`, or supplied explicitly |
| `details` | Optional free-text note |

## Python API

```python
from pathlib import Path
from envault.commands.audit import record_event, read_events, format_events

vault = Path("production.vault")

# Record an event
record_event(vault, "set", key="DB_PASSWORD", actor="alice")

# Read all events
events = read_events(vault)

# Pretty-print
print(format_events(events))
```

## Example output

```
2024-06-01T12:00:00+00:00  alice         set                  [DB_PASSWORD]
2024-06-01T12:05:32+00:00  ci            rotate               — scheduled rotation
2024-06-01T14:22:11+00:00  bob           export               [API_KEY]
```

## Clearing the log

```python
from envault.commands.audit import clear_log

removed = clear_log(vault)
print(f"Cleared {removed} audit events.")
```

> **Note:** The audit log is intentionally kept outside the encrypted
> vault so it remains readable without the passphrase. Do not store
> sensitive values in the `details` field.
