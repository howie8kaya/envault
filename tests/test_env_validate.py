import pytest
from pathlib import Path

from envault.vault import init_vault, set_secret
from envault.commands.env_validate import (
    validate_type,
    validate_vault_types,
    format_validation_results,
    EnvValidateError,
)


@pytest.fixture
def vault_path(tmp_path):
    p = tmp_path / "test.vault"
    init_vault(p, "pass")
    set_secret(p, "pass", "DATABASE_URL", "https://db.example.com/mydb")
    set_secret(p, "pass", "PORT", "5432")
    set_secret(p, "pass", "DEBUG", "true")
    set_secret(p, "pass", "API_KEY", "abc123")
    set_secret(p, "pass", "EMPTY_VAL", "")
    return p


def test_validate_type_url_valid():
    assert validate_type("https://example.com", "url") is True


def test_validate_type_url_invalid():
    assert validate_type("not-a-url", "url") is False


def test_validate_type_integer_valid():
    assert validate_type("42", "integer") is True
    assert validate_type("-7", "integer") is True


def test_validate_type_integer_invalid():
    assert validate_type("3.14", "integer") is False


def test_validate_type_boolean_valid():
    for v in ["true", "false", "1", "0", "yes", "no", "True", "FALSE"]:
        assert validate_type(v, "boolean") is True


def test_validate_type_boolean_invalid():
    assert validate_type("maybe", "boolean") is False


def test_validate_type_email_valid():
    assert validate_type("user@example.com", "email") is True


def test_validate_type_email_invalid():
    assert validate_type("not-an-email", "email") is False


def test_validate_type_unknown_raises():
    with pytest.raises(EnvValidateError, match="Unknown type"):
        validate_type("value", "banana")


def test_validate_vault_types_all_pass(vault_path):
    rules = {"DATABASE_URL": "url", "PORT": "integer", "DEBUG": "boolean"}
    results = validate_vault_types(vault_path, "pass", rules)
    assert all(r.passed for r in results)
    assert len(results) == 3


def test_validate_vault_types_fail_on_wrong_type(vault_path):
    rules = {"PORT": "url"}
    results = validate_vault_types(vault_path, "pass", rules)
    assert len(results) == 1
    assert results[0].passed is False
    assert "url" in results[0].message


def test_validate_vault_types_missing_key(vault_path):
    rules = {"NONEXISTENT_KEY": "integer"}
    results = validate_vault_types(vault_path, "pass", rules)
    assert results[0].passed is False
    assert "not found" in results[0].message


def test_validate_vault_types_empty_rules(vault_path):
    results = validate_vault_types(vault_path, "pass", {})
    assert results == []


def test_format_validation_results_no_rules():
    assert format_validation_results([]) == "No rules to validate."


def test_format_validation_results_shows_pass_fail(vault_path):
    rules = {"PORT": "integer", "DATABASE_URL": "integer"}
    results = validate_vault_types(vault_path, "pass", rules)
    output = format_validation_results(results)
    assert "PASS" in output
    assert "FAIL" in output


def test_result_str_format(vault_path):
    rules = {"PORT": "integer"}
    results = validate_vault_types(vault_path, "pass", rules)
    s = str(results[0])
    assert "[PASS]" in s
    assert "PORT" in s
    assert "integer" in s
