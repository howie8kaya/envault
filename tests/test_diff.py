"""Tests for envault.commands.diff."""

import json
import os
import pytest

from envault.commands.diff import diff_vault_vs_file, format_diff, DiffEntry
from envault.vault import init_vault, set_secret
from envault.vault import VaultError


PASSPHRASE = "test-passphrase"


@pytest.fixture
def vault_path(tmp_path):
    path = str(tmp_path / "test.vault")
    init_vault(path, PASSPHRASE)
    return path


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("KEY1=hello\nKEY2=world\n")
    return str(p)


def test_diff_identical(vault_path, env_file):
    set_secret(vault_path, "KEY1", "hello", PASSPHRASE)
    set_secret(vault_path, "KEY2", "world", PASSPHRASE)
    entries = diff_vault_vs_file(vault_path, env_file, PASSPHRASE, show_unchanged=True)
    statuses = {e.key: e.status for e in entries}
    assert statuses["KEY1"] == "unchanged"
    assert statuses["KEY2"] == "unchanged"


def test_diff_changed_value(vault_path, env_file):
    set_secret(vault_path, "KEY1", "different", PASSPHRASE)
    set_secret(vault_path, "KEY2", "world", PASSPHRASE)
    entries = diff_vault_vs_file(vault_path, env_file, PASSPHRASE)
    statuses = {e.key: e.status for e in entries}
    assert statuses["KEY1"] == "changed"
    assert "KEY2" not in statuses  # unchanged, filtered out


def test_diff_key_only_in_vault(vault_path, env_file):
    set_secret(vault_path, "KEY1", "hello", PASSPHRASE)
    set_secret(vault_path, "KEY2", "world", PASSPHRASE)
    set_secret(vault_path, "EXTRA", "secret", PASSPHRASE)
    entries = diff_vault_vs_file(vault_path, env_file, PASSPHRASE)
    statuses = {e.key: e.status for e in entries}
    assert statuses["EXTRA"] == "removed"


def test_diff_key_only_in_file(vault_path, env_file):
    set_secret(vault_path, "KEY1", "hello", PASSPHRASE)
    # KEY2 not in vault
    entries = diff_vault_vs_file(vault_path, env_file, PASSPHRASE)
    statuses = {e.key: e.status for e in entries}
    assert statuses["KEY2"] == "added"


def test_diff_wrong_passphrase_raises(vault_path, env_file):
    set_secret(vault_path, "KEY1", "hello", PASSPHRASE)
    with pytest.raises(VaultError):
        diff_vault_vs_file(vault_path, env_file, "wrong-passphrase")


def test_diff_missing_env_raises(vault_path, env_file):
    with pytest.raises(VaultError, match="Environment 'staging' not found"):
        diff_vault_vs_file(vault_path, env_file, PASSPHRASE, env_name="staging")


def test_format_diff_no_entries():
    assert format_diff([]) == "No differences found."


def test_format_diff_shows_symbols(vault_path, env_file):
    set_secret(vault_path, "KEY1", "changed_val", PASSPHRASE)
    entries = diff_vault_vs_file(vault_path, env_file, PASSPHRASE)
    output = format_diff(entries)
    assert "~" in output or "+" in output or "-" in output


def test_diff_entry_str_representations():
    assert str(DiffEntry("A", "added")) == "+ A  (only in file)"
    assert str(DiffEntry("B", "removed")) == "- B  (only in vault)"
    assert str(DiffEntry("C", "changed")) == "~ C  (vault != file)"
    assert str(DiffEntry("D", "unchanged")) == "  D  (same)"
