"""Tests for envault.commands.env_audit_export."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envault.commands.audit import record_event
from envault.commands.env_audit_export import (
    AuditExportError,
    AuditExportResult,
    export_audit,
)
from envault.vault import init_vault


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    p = tmp_path / "test.vault"
    init_vault(p, "secret")
    return p


def _populate(vault_path: Path) -> None:
    record_event(vault_path, "set", key="DB_URL", user="alice")
    record_event(vault_path, "delete", key="OLD_KEY", user="bob")
    record_event(vault_path, "rotate", user="alice")


def test_export_json_returns_result(vault_path: Path) -> None:
    _populate(vault_path)
    result = export_audit(vault_path, fmt="json")
    assert isinstance(result, AuditExportResult)
    assert result.format == "json"
    assert result.entry_count == 3


def test_export_json_is_valid_json(vault_path: Path) -> None:
    _populate(vault_path)
    result = export_audit(vault_path, fmt="json")
    parsed = json.loads(result.output)
    assert isinstance(parsed, list)
    assert len(parsed) == 3


def test_export_csv_contains_header(vault_path: Path) -> None:
    _populate(vault_path)
    result = export_audit(vault_path, fmt="csv")
    assert "action" in result.output or "timestamp" in result.output


def test_export_csv_row_count(vault_path: Path) -> None:
    _populate(vault_path)
    result = export_audit(vault_path, fmt="csv")
    lines = [l for l in result.output.strip().splitlines() if l]
    # header + 3 data rows
    assert len(lines) == 4


def test_export_text_format(vault_path: Path) -> None:
    _populate(vault_path)
    result = export_audit(vault_path, fmt="text")
    assert result.entry_count == 3
    assert "set" in result.output
    assert "delete" in result.output


def test_export_empty_vault_returns_zero(vault_path: Path) -> None:
    result = export_audit(vault_path, fmt="json")
    assert result.entry_count == 0
    assert json.loads(result.output) == []


def test_export_empty_text_placeholder(vault_path: Path) -> None:
    result = export_audit(vault_path, fmt="text")
    assert "(no events)" in result.output


def test_export_filter_by_keys(vault_path: Path) -> None:
    _populate(vault_path)
    result = export_audit(vault_path, fmt="json", keys=["DB_URL"])
    parsed = json.loads(result.output)
    assert result.entry_count == 1
    assert parsed[0]["key"] == "DB_URL"


def test_export_filter_since(vault_path: Path) -> None:
    record_event(vault_path, "set", key="EARLY", user="x")
    events_all = export_audit(vault_path, fmt="json")
    all_parsed = json.loads(events_all.output)
    # Use the timestamp of the last event as the cutoff
    last_ts = all_parsed[-1]["timestamp"]
    result = export_audit(vault_path, fmt="json", since=last_ts)
    assert result.entry_count >= 1


def test_export_unsupported_format_raises(vault_path: Path) -> None:
    with pytest.raises(AuditExportError, match="Unsupported format"):
        export_audit(vault_path, fmt="xml")


def test_result_str(vault_path: Path) -> None:
    _populate(vault_path)
    result = export_audit(vault_path, fmt="csv")
    assert "3" in str(result)
    assert "csv" in str(result)
