# Schema Validation

envault supports validating vault secrets against a schema of rules.

## Overview

Define rules for each key you expect in the vault — whether it's required,
what pattern it should match, and length constraints.

## Usage

```python
from envault.commands.schema import SchemaRule, validate_vault, format_schema_results

rules = [
    SchemaRule(key="API_KEY", required=True, pattern=r"[A-Za-z0-9]{32}"),
    SchemaRule(key="DB_URL", required=True, min_length=10),
    SchemaRule(key="DEBUG", required=False),
]

issues = validate_vault("prod.vault", "my-passphrase", rules)
print(format_schema_results(issues))
```

## SchemaRule Fields

| Field        | Type   | Default | Description                          |
|--------------|--------|---------|--------------------------------------|
| `key`        | str    | —       | The secret key to validate           |
| `required`   | bool   | True    | Whether the key must exist           |
| `pattern`    | str    | None    | Regex pattern the value must match   |
| `min_length` | int    | 0       | Minimum value length (0 = no limit)  |
| `max_length` | int    | 0       | Maximum value length (0 = no limit)  |

## Issue Severities

- **error** — validation failed (missing required key, pattern mismatch, length violation)

## Output Example

```
[ERROR] API_KEY: value does not match pattern '[A-Za-z0-9]{32}'
[ERROR] DB_URL: required key is missing
```

If all rules pass:

```
Schema validation passed.
```
