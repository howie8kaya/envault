"""Tests for envault.env_io — .env parsing and serialization."""

import pytest
from pathlib import Path
from envault.env_io import (
    parse_env,
    serialize_env,
    read_env_file,
    write_env_file,
    EnvParseError,
)


def test_parse_simple_key_value():
    result = parse_env("FOO=bar\nBAZ=qux\n")
    assert result == {"FOO": "bar", "BAZ": "qux"}


def test_parse_ignores_comments_and_blank_lines():
    text = "\n# This is a comment\nKEY=value\n\n"
    assert parse_env(text) == {"KEY": "value"}


def test_parse_strips_double_quotes():
    assert parse_env('DB_URL="postgres://localhost"') == {
        "DB_URL": "postgres://localhost"
    }


def test_parse_strips_single_quotes():
    assert parse_env("SECRET='mysecret'") == {"SECRET": "mysecret"}


def test_parse_value_with_equals_sign():
    result = parse_env("TOKEN=abc=def=ghi")
    assert result["TOKEN"] == "abc=def=ghi"


def test_parse_missing_equals_raises():
    with pytest.raises(EnvParseError, match="missing '='"):
        parse_env("BADLINE")


def test_parse_empty_key_raises():
    with pytest.raises(EnvParseError, match="empty key"):
        parse_env("=value")


def test_serialize_sorted_output():
    result = serialize_env({"ZEBRA": "1", "ALPHA": "2"})
    lines = result.strip().splitlines()
    assert lines[0].startswith("ALPHA")
    assert lines[1].startswith("ZEBRA")


def test_serialize_quotes_values_with_spaces():
    result = serialize_env({"MSG": "hello world"})
    assert 'MSG="hello world"' in result


def test_serialize_empty_dict():
    assert serialize_env({}) == ""


def test_roundtrip_parse_serialize():
    original = {"API_KEY": "abc123", "DEBUG": "true", "URL": "http://example.com"}
    serialized = serialize_env(original)
    parsed = parse_env(serialized)
    assert parsed == original


def test_read_env_file(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("PORT=8080\nHOST=localhost\n", encoding="utf-8")
    result = read_env_file(env_file)
    assert result == {"PORT": "8080", "HOST": "localhost"}


def test_read_env_file_not_found(tmp_path):
    with pytest.raises(EnvParseError, match="File not found"):
        read_env_file(tmp_path / "missing.env")


def test_write_env_file(tmp_path):
    env_file = tmp_path / ".env"
    write_env_file(env_file, {"FOO": "bar"})
    assert env_file.read_text(encoding="utf-8") == "FOO=bar\n"
