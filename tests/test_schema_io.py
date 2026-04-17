import json
import pytest
from pathlib import Path
from envault.commands.schema import SchemaRule, SchemaError
from envault.commands.schema_io import load_schema, save_schema


@pytest.fixture
def schema_file(tmp_path):
    return str(tmp_path / "schema.json")


def test_save_and_load_roundtrip(schema_file):
    rules = [
        SchemaRule(key="API_KEY", required=True, pattern=r"[a-z]+"),
        SchemaRule(key="PORT", required=False, min_length=1, max_length=5),
    ]
    save_schema(rules, schema_file)
    loaded = load_schema(schema_file)
    assert len(loaded) == 2
    assert loaded[0].key == "API_KEY"
    assert loaded[0].pattern == r"[a-z]+"
    assert loaded[1].required is False
    assert loaded[1].max_length == 5


def test_load_missing_file_raises(tmp_path):
    with pytest.raises(SchemaError, match="not found"):
        load_schema(str(tmp_path / "nonexistent.json"))


def test_load_invalid_json_raises(schema_file):
    Path(schema_file).write_text("not json{{{")
    with pytest.raises(SchemaError, match="Invalid JSON"):
        load_schema(schema_file)


def test_load_non_array_raises(schema_file):
    Path(schema_file).write_text(json.dumps({"key": "API_KEY"}))
    with pytest.raises(SchemaError, match="array"):
        load_schema(schema_file)


def test_load_rule_missing_key_raises(schema_file):
    Path(schema_file).write_text(json.dumps([{"required": True}]))
    with pytest.raises(SchemaError, match="missing 'key'"):
        load_schema(schema_file)


def test_save_omits_defaults(schema_file):
    rules = [SchemaRule(key="FOO")]
    save_schema(rules, schema_file)
    data = json.loads(Path(schema_file).read_text())
    assert data[0] == {"key": "FOO", "required": True}


def test_load_defaults_applied(schema_file):
    Path(schema_file).write_text(json.dumps([{"key": "BAR"}]))
    rules = load_schema(schema_file)
    assert rules[0].required is True
    assert rules[0].pattern is None
    assert rules[0].min_length == 0
