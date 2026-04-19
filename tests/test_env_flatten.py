import json
import pytest
from pathlib import Path
from envault.vault import init_vault, set_secret, get_secret, load_vault
from envault.commands.env_flatten import flatten_secret, FlattenError

PASS = "testpass"


@pytest.fixture
def vault_path(tmp_path):
    p = tmp_path / "test.vault"
    init_vault(str(p), PASS)
    return str(p)


def _set(vault_path, key, value):
    vault = load_vault(vault_path, PASS)
    vault = set_secret(vault, PASS, key, value)
    from envault.vault import save_vault
    save_vault(vault_path, vault)


def test_flatten_simple_object(vault_path):
    _set(vault_path, "DB", json.dumps({"host": "localhost", "port": "5432"}))
    result = flatten_secret(vault_path, PASS, "DB")
    assert "DB__host" in result.flattened
    assert "DB__port" in result.flattened


def test_flatten_values_readable(vault_path):
    _set(vault_path, "DB", json.dumps({"host": "myhost"}))
    flatten_secret(vault_path, PASS, "DB")
    vault = load_vault(vault_path, PASS)
    val = get_secret(vault, PASS, "DB__host")
    assert val == "myhost"


def test_flatten_nested_object(vault_path):
    _set(vault_path, "CFG", json.dumps({"a": {"b": "deep"}}))
    result = flatten_secret(vault_path, PASS, "CFG")
    assert "CFG__a__b" in result.flattened
    assert result.flattened["CFG__a__b"] == "deep"


def test_flatten_custom_prefix(vault_path):
    _set(vault_path, "CFG", json.dumps({"key": "val"}))
    result = flatten_secret(vault_path, PASS, "CFG", prefix="APP")
    assert "APP__key" in result.flattened


def test_flatten_custom_sep(vault_path):
    _set(vault_path, "CFG", json.dumps({"x": "1"}))
    result = flatten_secret(vault_path, PASS, "CFG", sep="_")
    assert "CFG_x" in result.flattened


def test_flatten_skips_existing_without_overwrite(vault_path):
    _set(vault_path, "DB", json.dumps({"host": "a"}))
    _set(vault_path, "DB__host", "existing")
    result = flatten_secret(vault_path, PASS, "DB")
    assert "DB__host" in result.skipped
    assert "DB__host" not in result.flattened


def test_flatten_overwrites_when_flag_set(vault_path):
    _set(vault_path, "DB", json.dumps({"host": "new"}))
    _set(vault_path, "DB__host", "old")
    result = flatten_secret(vault_path, PASS, "DB", overwrite=True)
    assert "DB__host" in result.flattened


def test_flatten_non_json_raises(vault_path):
    _set(vault_path, "PLAIN", "not-json")
    with pytest.raises(FlattenError, match="not valid JSON"):
        flatten_secret(vault_path, PASS, "PLAIN")


def test_flatten_json_array_raises(vault_path):
    _set(vault_path, "ARR", json.dumps([1, 2, 3]))
    with pytest.raises(FlattenError, match="JSON object"):
        flatten_secret(vault_path, PASS, "ARR")


def test_flatten_str_result(vault_path):
    _set(vault_path, "S", json.dumps({"a": "1"}))
    result = flatten_secret(vault_path, PASS, "S")
    assert "S__a" in str(result)
