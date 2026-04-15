"""Tests for envault.commands.audit."""

import pytest
from pathlib import Path

from envault.commands.audit import (
    record_event,
    read_events,
    clear_log,
    format_events,
    AUDIT_LOG_FILENAME,
)


@pytest.fixture
def vault_path(tmp_path: Path) -> Path:
    p = tmp_path / "test.vault"
    p.write_text("{}")
    return p


def test_record_event_creates_log(vault_path):
    record_event(vault_path, "set", key="DB_URL", actor="alice")
    log = vault_path.parent / AUDIT_LOG_FILENAME
    assert log.exists()


def test_record_event_returns_dict(vault_path):
    event = record_event(vault_path, "init", actor="bob")
    assert event["action"] == "init"
    assert event["actor"] == "bob"
    assert "timestamp" in event


def test_read_events_empty_when_no_log(vault_path):
    events = read_events(vault_path)
    assert events == []


def test_read_events_returns_all_recorded(vault_path):
    record_event(vault_path, "set", key="FOO", actor="alice")
    record_event(vault_path, "get", key="FOO", actor="bob")
    record_event(vault_path, "delete", key="FOO", actor="alice")
    events = read_events(vault_path)
    assert len(events) == 3
    assert events[0]["action"] == "set"
    assert events[2]["action"] == "delete"


def test_event_key_and_details_stored(vault_path):
    record_event(vault_path, "rotate", key=None, actor="ci", details="scheduled rotation")
    events = read_events(vault_path)
    assert events[0]["details"] == "scheduled rotation"
    assert events[0]["key"] is None


def test_clear_log_removes_file(vault_path):
    record_event(vault_path, "set", key="X")
    count = clear_log(vault_path)
    assert count == 1
    log = vault_path.parent / AUDIT_LOG_FILENAME
    assert not log.exists()


def test_clear_log_on_missing_log_returns_zero(vault_path):
    count = clear_log(vault_path)
    assert count == 0


def test_format_events_no_events():
    result = format_events([])
    assert "No audit" in result


def test_format_events_contains_action(vault_path):
    record_event(vault_path, "export", key="SECRET", actor="dev")
    events = read_events(vault_path)
    output = format_events(events)
    assert "export" in output
    assert "SECRET" in output
    assert "dev" in output


def test_multiple_vaults_have_separate_logs(tmp_path):
    vault_a = tmp_path / "a" / "a.vault"
    vault_b = tmp_path / "b" / "b.vault"
    vault_a.parent.mkdir()
    vault_b.parent.mkdir()
    vault_a.write_text("{}")
    vault_b.write_text("{}")

    record_event(vault_a, "set", key="A_KEY")
    record_event(vault_b, "set", key="B_KEY")

    assert len(read_events(vault_a)) == 1
    assert len(read_events(vault_b)) == 1
    assert read_events(vault_a)[0]["key"] == "A_KEY"
    assert read_events(vault_b)[0]["key"] == "B_KEY"
