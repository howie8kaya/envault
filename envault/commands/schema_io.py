"""Load and save schema rule definitions from JSON files."""
from __future__ import annotations
import json
from pathlib import Path
from envault.commands.schema import SchemaRule, SchemaError


DEFAULT_SCHEMA_FILE = ".envault-schema.json"


def load_schema(path: str = DEFAULT_SCHEMA_FILE) -> list[SchemaRule]:
    """Load schema rules from a JSON file."""
    p = Path(path)
    if not p.exists():
        raise SchemaError(f"Schema file not found: {path}")
    try:
        data = json.loads(p.read_text())
    except json.JSONDecodeError as e:
        raise SchemaError(f"Invalid JSON in schema file: {e}") from e

    if not isinstance(data, list):
        raise SchemaError("Schema file must contain a JSON array of rule objects")

    rules = []
    for item in data:
        if "key" not in item:
            raise SchemaError(f"Schema rule missing 'key' field: {item}")
        rules.append(SchemaRule(
            key=item["key"],
            required=item.get("required", True),
            pattern=item.get("pattern", None),
            min_length=item.get("min_length", 0),
            max_length=item.get("max_length", 0),
        ))
    return rules


def save_schema(rules: list[SchemaRule], path: str = DEFAULT_SCHEMA_FILE) -> None:
    """Save schema rules to a JSON file."""
    data = [
        {
            "key": r.key,
            "required": r.required,
            **(  {"pattern": r.pattern} if r.pattern else {}),
            **(  {"min_length": r.min_length} if r.min_length else {}),
            **(  {"max_length": r.max_length} if r.max_length else {}),
        }
        for r in rules
    ]
    Path(path).write_text(json.dumps(data, indent=2))
