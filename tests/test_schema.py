import pytest
import os
from envault.vault import init_vault, set_secret
from envault.commands.schema import (
    SchemaRule, ValidationIssue, validate_vault, format_schema_results
)

PASS = "testpass"


@pytest.fixture
def vault_path(tmp_path):
    p = str(tmp_path / "test.vault")
    init_vault(p, PASS)
    set_secret(p, "API_KEY", "abc123", PASS)
    set_secret(p, "DB_URL", "postgres://localhost/db", PASS)
    return p


def test_validate_passes_when_all_rules_met(vault_path):
    rules = [SchemaRule(key="API_KEY"), SchemaRule(key="DB_URL")]
    issues = validate_vault(vault_path, PASS, rules)
    assert issues == []


def test_missing_required_key_is_error(vault_path):
    rules = [SchemaRule(key="MISSING_KEY", required=True)]
    issues = validate_vault(vault_path, PASS, rules)
    assert len(issues) == 1
    assert issues[0].severity == "error"
    assert "missing" in issues[0].message


def test_missing_optional_key_no_issue(vault_path):
    rules = [SchemaRule(key="OPTIONAL", required=False)]
    issues = validate_vault(vault_path, PASS, rules)
    assert issues == []


def test_pattern_match_passes(vault_path):
    rules = [SchemaRule(key="API_KEY", pattern=r"[a-z0-9]+")]
    issues = validate_vault(vault_path, PASS, rules)
    assert issues == []


def test_pattern_mismatch_is_error(vault_path):
    rules = [SchemaRule(key="API_KEY", pattern=r"\d{10}")]
    issues = validate_vault(vault_path, PASS, rules)
    assert len(issues) == 1
    assert "pattern" in issues[0].message


def test_min_length_violation(vault_path):
    rules = [SchemaRule(key="API_KEY", min_length=100)]
    issues = validate_vault(vault_path, PASS, rules)
    assert any("too short" in i.message for i in issues)


def test_max_length_violation(vault_path):
    rules = [SchemaRule(key="API_KEY", max_length=2)]
    issues = validate_vault(vault_path, PASS, rules)
    assert any("too long" in i.message for i in issues)


def test_format_schema_results_no_issues():
    assert format_schema_results([]) == "Schema validation passed."


def test_format_schema_results_with_issues():
    issues = [ValidationIssue("KEY", "error", "required key is missing")]
    out = format_schema_results(issues)
    assert "[ERROR]" in out
    assert "KEY" in out


def test_validation_issue_str():
    issue = ValidationIssue("FOO", "warning", "some warning")
    assert str(issue) == "[WARNING] FOO: some warning"
