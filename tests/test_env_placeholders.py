"""Tests for envault.commands.env_placeholders."""

import pytest
from pathlib import Path

from envault.vault import init_vault, set_secret
from envault.commands.env_placeholders import (
    find_placeholders,
    PlaceholderError,
    PlaceholderEntry,
    PlaceholderResult,
)


PASSPHRASE = "test-pass"


@pytest.fixture
def vault_path(tmp_path: Path) -> str:
    p = str(tmp_path / "test.vault")
    init_vault(p, PASSPHRASE)
    return p


def test_find_placeholders_no_placeholders(vault_path):
    set_secret(vault_path, PASSPHRASE, "API_KEY", "abc123")
    result = find_placeholders(vault_path, PASSPHRASE)
    assert result.clean is True
    assert result.count == 0
    assert result.total_keys == 1


def test_find_placeholders_detects_angle_bracket(vault_path):
    set_secret(vault_path, PASSPHRASE, "DB_PASS", "<your-password-here>")
    result = find_placeholders(vault_path, PASSPHRASE)
    assert result.count == 1
    assert result.entries[0].key == "DB_PASS"


def test_find_placeholders_detects_mustache(vault_path):
    set_secret(vault_path, PASSPHRASE, "SECRET", "{{REPLACE_ME}}")
    result = find_placeholders(vault_path, PASSPHRASE)
    assert result.count == 1
    assert result.entries[0].key == "SECRET"


def test_find_placeholders_detects_change_me(vault_path):
    set_secret(vault_path, PASSPHRASE, "TOKEN", "CHANGE_ME")
    result = find_placeholders(vault_path, PASSPHRASE)
    assert result.count == 1


def test_find_placeholders_detects_todo(vault_path):
    set_secret(vault_path, PASSPHRASE, "WEBHOOK", "TODO")
    result = find_placeholders(vault_path, PASSPHRASE)
    assert result.count == 1


def test_find_placeholders_case_insensitive(vault_path):
    set_secret(vault_path, PASSPHRASE, "VAR", "fixme")
    result = find_placeholders(vault_path, PASSPHRASE)
    assert result.count == 1


def test_find_placeholders_mixed(vault_path):
    set_secret(vault_path, PASSPHRASE, "REAL", "supersecret")
    set_secret(vault_path, PASSPHRASE, "FAKE", "<fill-me-in>")
    result = find_placeholders(vault_path, PASSPHRASE)
    assert result.count == 1
    assert result.entries[0].key == "FAKE"
    assert result.total_keys == 2


def test_find_placeholders_selective_keys(vault_path):
    set_secret(vault_path, PASSPHRASE, "A", "<placeholder>")
    set_secret(vault_path, PASSPHRASE, "B", "<placeholder>")
    result = find_placeholders(vault_path, PASSPHRASE, keys=["A"])
    assert result.count == 1
    assert result.total_keys == 1


def test_find_placeholders_missing_key_raises(vault_path):
    set_secret(vault_path, PASSPHRASE, "A", "value")
    with pytest.raises(PlaceholderError, match="MISSING"):
        find_placeholders(vault_path, PASSPHRASE, keys=["MISSING"])


def test_placeholder_result_str_clean(vault_path):
    set_secret(vault_path, PASSPHRASE, "X", "realvalue")
    result = find_placeholders(vault_path, PASSPHRASE)
    assert "No placeholders" in str(result)


def test_placeholder_result_str_with_entries(vault_path):
    set_secret(vault_path, PASSPHRASE, "Y", "<todo>")
    result = find_placeholders(vault_path, PASSPHRASE)
    assert "1 placeholder" in str(result)
    assert "Y" in str(result)


def test_placeholder_entry_str():
    entry = PlaceholderEntry(key="FOO", value="<bar>", pattern_matched="<bar>")
    assert "FOO" in str(entry)
    assert "<bar>" in str(entry)
