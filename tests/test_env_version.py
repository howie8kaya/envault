"""Tests for envault/commands/env_version.py"""

import pytest

from envault.vault import init_vault, set_secret
from envault.commands.env_version import (
    VersionError,
    VersionEntry,
    record_version,
    get_versions,
    rollback,
)


@pytest.fixture
def vault_path(tmp_path):
    p = tmp_path / "test.vault"
    init_vault(str(p), "pass123")
    set_secret(str(p), "pass123", "API_KEY", "initial_value")
    return str(p)


def test_record_version_returns_entry(vault_path):
    entry = record_version(vault_path, "pass123", "API_KEY")
    assert isinstance(entry, VersionEntry)
    assert entry.version == 1
    assert entry.value == "initial_value"


def test_record_version_increments(vault_path):
    record_version(vault_path, "pass123", "API_KEY")
    set_secret(vault_path, "pass123", "API_KEY", "second_value")
    entry = record_version(vault_path, "pass123", "API_KEY")
    assert entry.version == 2
    assert entry.value == "second_value"


def test_record_version_with_note(vault_path):
    entry = record_version(vault_path, "pass123", "API_KEY", note="before rotation")
    assert entry.note == "before rotation"


def test_record_version_missing_key_raises(vault_path):
    with pytest.raises(VersionError, match="MISSING"):
        record_version(vault_path, "pass123", "MISSING")


def test_get_versions_empty_when_none(vault_path):
    versions = get_versions(vault_path, "pass123", "API_KEY")
    assert versions == []


def test_get_versions_returns_all_recorded(vault_path):
    record_version(vault_path, "pass123", "API_KEY", note="v1")
    set_secret(vault_path, "pass123", "API_KEY", "value2")
    record_version(vault_path, "pass123", "API_KEY", note="v2")
    versions = get_versions(vault_path, "pass123", "API_KEY")
    assert len(versions) == 2
    assert versions[0].value == "initial_value"
    assert versions[1].value == "value2"


def test_version_entry_str_contains_version_number(vault_path):
    entry = record_version(vault_path, "pass123", "API_KEY")
    assert "v1" in str(entry)


def test_rollback_restores_value(vault_path):
    record_version(vault_path, "pass123", "API_KEY")
    set_secret(vault_path, "pass123", "API_KEY", "updated_value")
    rollback(vault_path, "pass123", "API_KEY", version=1)
    from envault.vault import get_secret
    assert get_secret(vault_path, "pass123", "API_KEY") == "initial_value"


def test_rollback_missing_version_raises(vault_path):
    record_version(vault_path, "pass123", "API_KEY")
    with pytest.raises(VersionError, match="Version 99"):
        rollback(vault_path, "pass123", "API_KEY", version=99)


def test_rollback_no_history_raises(vault_path):
    with pytest.raises(VersionError, match="No version history"):
        rollback(vault_path, "pass123", "API_KEY", version=1)


def test_recorded_at_is_recent(vault_path):
    import time
    before = time.time()
    entry = record_version(vault_path, "pass123", "API_KEY")
    after = time.time()
    assert before <= entry.recorded_at <= after
