"""Tests for envault.commands.search."""

import json
import pytest

from envault.vault import init_vault, set_secret
from envault.commands.search import search_vault, format_search_results, SearchResult


@pytest.fixture
def vault_path(tmp_path):
    path = str(tmp_path / "test.vault")
    init_vault(path, passphrase="hunter2")
    set_secret(path, "DB_HOST", "localhost", "hunter2")
    set_secret(path, "DB_PASSWORD", "s3cr3t", "hunter2")
    set_secret(path, "API_KEY", "abc123", "hunter2")
    set_secret(path, "API_SECRET", "xyz789", "hunter2")
    return path


def test_search_by_key_substring(vault_path):
    results = search_vault(vault_path, "hunter2", "DB")
    keys = [r.key for r in results]
    assert "DB_HOST" in keys
    assert "DB_PASSWORD" in keys
    assert "API_KEY" not in keys


def test_search_by_key_glob(vault_path):
    results = search_vault(vault_path, "hunter2", "API_*", glob_mode=True)
    keys = [r.key for r in results]
    assert "API_KEY" in keys
    assert "API_SECRET" in keys
    assert "DB_HOST" not in keys


def test_search_no_matches(vault_path):
    results = search_vault(vault_path, "hunter2", "NONEXISTENT")
    assert results == []


def test_search_match_type_is_key(vault_path):
    results = search_vault(vault_path, "hunter2", "API_KEY")
    assert len(results) == 1
    assert results[0].match_type == "key"


def test_search_values_finds_match(vault_path):
    results = search_vault(vault_path, "hunter2", "abc123", search_values=True)
    assert any(r.key == "API_KEY" for r in results)


def test_search_values_match_type_value(vault_path):
    results = search_vault(vault_path, "hunter2", "abc123", search_values=True)
    match = next(r for r in results if r.key == "API_KEY")
    assert match.match_type == "value"


def test_search_case_insensitive_by_default(vault_path):
    results = search_vault(vault_path, "hunter2", "db_host")
    keys = [r.key for r in results]
    assert "DB_HOST" in keys


def test_search_case_sensitive_no_match(vault_path):
    results = search_vault(vault_path, "hunter2", "db_host", case_sensitive=True)
    assert results == []


def test_format_search_results_empty():
    assert format_search_results([]) == "No matches found."


def test_format_search_results_masks_value():
    r = SearchResult(key="MY_KEY", value="supersecret", match_type="key")
    output = format_search_results([r])
    assert "supe****" in output
    assert "supersecret" not in output


def test_format_search_results_reveal():
    r = SearchResult(key="MY_KEY", value="supersecret", match_type="key")
    output = format_search_results([r], reveal=True)
    assert "supersecret" in output
