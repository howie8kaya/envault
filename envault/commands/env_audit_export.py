"""Export audit log entries to various formats (JSON, CSV, plain text)."""

from __future__ import annotations

import csv
import io
import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from envault.commands.audit import read_events


class AuditExportError(Exception):
    pass


@dataclass
class AuditExportResult:
    format: str
    entry_count: int
    output: str

    def __str__(self) -> str:
        return f"Exported {self.entry_count} audit event(s) as {self.format}"


def export_audit(
    vault_path: Path,
    fmt: str = "json",
    keys: Optional[List[str]] = None,
    since: Optional[str] = None,
) -> AuditExportResult:
    """Export audit log entries from a vault to the requested format.

    Args:
        vault_path: Path to the vault file.
        fmt: Output format — 'json', 'csv', or 'text'.
        keys: If provided, only include events whose 'key' field matches.
        since: ISO timestamp string; exclude events before this time.

    Returns:
        AuditExportResult with the serialised output.
    """
    if fmt not in ("json", "csv", "text"):
        raise AuditExportError(f"Unsupported format: {fmt!r}. Choose json, csv, or text.")

    events = read_events(vault_path)

    if keys is not None:
        key_set = set(keys)
        events = [e for e in events if e.get("key") in key_set]

    if since is not None:
        events = [e for e in events if e.get("timestamp", "") >= since]

    if fmt == "json":
        output = json.dumps(events, indent=2)
    elif fmt == "csv":
        output = _to_csv(events)
    else:
        output = _to_text(events)

    return AuditExportResult(format=fmt, entry_count=len(events), output=output)


def _to_csv(events: list) -> str:
    if not events:
        return ""
    fieldnames = list(dict.fromkeys(k for e in events for k in e))
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(events)
    return buf.getvalue()


def _to_text(events: list) -> str:
    if not events:
        return "(no events)"
    lines = []
    for e in events:
        ts = e.get("timestamp", "?")
        action = e.get("action", "?")
        key = e.get("key", "")
        user = e.get("user", "")
        parts = [f"[{ts}]", action]
        if key:
            parts.append(f"key={key}")
        if user:
            parts.append(f"user={user}")
        lines.append(" ".join(parts))
    return "\n".join(lines)
