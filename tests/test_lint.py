"""Tests for envault.commands.lint"""

import json
import pytest
from pathlib import Path

from envault.vault import init_vault, set_secret
from envault.commands.lint import lint_vault, format_lint_results, LintIssue


PASS = "supersecretpass"


@pytest.fixture
def vault_path(tmp_path):
    p = tmp_path / "test.vault"
    init_vault(str(p), PASS)
    return str(p)


def test_lint_clean_vault_returns_no_issues(vault_path):
    set_secret(vault_path, PASS, "DATABASE_URL", "postgres://user:hunter2@localhost/db")
    issues = lint_vault(vault_path, PASS)
    assert issues == []


def test_lint_empty_value_is_error(vault_path):
    set_secret(vault_path, PASS, "EMPTY_KEY", "")
    issues = lint_vault(vault_path, PASS)
    assert any(i.key == "EMPTY_KEY" and i.severity == "error" for i in issues)


def test_lint_placeholder_value_is_warning(vault_path):
    set_secret(vault_path, PASS, "API_TOKEN", "changeme")
    issues = lint_vault(vault_path, PASS)
    assert any(i.key == "API_TOKEN" and i.severity == "warning" for i in issues)


def test_lint_duplicate_values_flagged(vault_path):
    set_secret(vault_path, PASS, "KEY_A", "sharedvalue123")
    set_secret(vault_path, PASS, "KEY_B", "sharedvalue123")
    issues = lint_vault(vault_path, PASS)
    dup_issues = [i for i in issues if "duplicate" in i.message]
    assert len(dup_issues) >= 1


def test_lint_short_value_is_warning(vault_path):
    set_secret(vault_path, PASS, "SHORT_SECRET", "abc")
    issues = lint_vault(vault_path, PASS)
    assert any(i.key == "SHORT_SECRET" and "short" in i.message for i in issues)


def test_lint_generic_key_name_is_info(vault_path):
    set_secret(vault_path, PASS, "SECRET", "averylongenoughvalue")
    issues = lint_vault(vault_path, PASS)
    assert any(i.key == "SECRET" and i.severity == "info" for i in issues)


def test_lint_wrong_passphrase_returns_error(vault_path):
    set_secret(vault_path, PASS, "SOME_KEY", "somevalue")
    issues = lint_vault(vault_path, "wrongpass")
    assert any(i.severity == "error" and "decrypt" in i.message for i in issues)


def test_format_lint_no_issues():
    result = format_lint_results([], 5)
    assert "No issues" in result
    assert "5" in result


def test_format_lint_with_issues():
    issues = [LintIssue("FOO", "warning", "value looks like a placeholder")]
    result = format_lint_results(issues, 3)
    assert "1 issue" in result
    assert "FOO" in result
    assert "warning" in result.lower()


def test_lint_issue_str():
    issue = LintIssue("MY_KEY", "error", "something bad")
    s = str(issue)
    assert "MY_KEY" in s
    assert "ERROR" in s
    assert "something bad" in s
