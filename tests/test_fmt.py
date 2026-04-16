import pytest
import json
from pathlib import Path
from envault.vault import init_vault, set_secret, get_secret
from envault.commands.fmt import fmt_vault, format_fmt_results, FmtError

PASS = "testpass"


@pytest.fixture
def vault_path(tmp_path):
    p = tmp_path / "vault.json"
    init_vault(str(p), PASS)
    return str(p)


def test_fmt_uppercase_keys(vault_path):
    set_secret(vault_path, PASS, "db_host", "localhost")
    changes = fmt_vault(vault_path, PASS)
    assert any(c.old_key == "db_host" and c.new_key == "DB_HOST" for c in changes)


def test_fmt_already_normalized_returns_no_changes(vault_path):
    set_secret(vault_path, PASS, "DB_HOST", "localhost")
    changes = fmt_vault(vault_path, PASS)
    assert changes == []


def test_fmt_applies_changes_to_vault(vault_path):
    set_secret(vault_path, PASS, "api_key", "abc123")
    fmt_vault(vault_path, PASS)
    val = get_secret(vault_path, PASS, "API_KEY")
    assert val == "abc123"


def test_fmt_old_key_removed_after_rename(vault_path):
    from envault.vault import load_vault
    set_secret(vault_path, PASS, "old_key", "value")
    fmt_vault(vault_path, PASS)
    vault = load_vault(vault_path)
    assert "old_key" not in vault["secrets"]


def test_fmt_normalizes_value_whitespace(vault_path):
    set_secret(vault_path, PASS, "MY_VAR", "  hello  ")
    changes = fmt_vault(vault_path, PASS)
    assert any(c.value_changed for c in changes)
    val = get_secret(vault_path, PASS, "MY_VAR")
    assert val == "hello"


def test_fmt_keys_only_skips_value_normalization(vault_path):
    set_secret(vault_path, PASS, "MY_VAR", "  hello  ")
    changes = fmt_vault(vault_path, PASS, keys_only=True)
    assert all(not c.value_changed for c in changes)
    val = get_secret(vault_path, PASS, "MY_VAR")
    assert val == "  hello  "


def test_fmt_dry_run_makes_no_changes(vault_path):
    from envault.vault import load_vault
    set_secret(vault_path, PASS, "lower_key", "value")
    vault_before = json.dumps(load_vault(vault_path), sort_keys=True)
    changes = fmt_vault(vault_path, PASS, dry_run=True)
    vault_after = json.dumps(load_vault(vault_path), sort_keys=True)
    assert changes  # changes detected
    assert vault_before == vault_after  # but nothing written


def test_format_fmt_results_empty():
    assert format_fmt_results([]) == "Vault is already normalized."


def test_format_fmt_results_lists_changes(vault_path):
    set_secret(vault_path, PASS, "foo_bar", "val")
    changes = fmt_vault(vault_path, PASS)
    output = format_fmt_results(changes)
    assert "foo_bar" in output
    assert "FOO_BAR" in output
