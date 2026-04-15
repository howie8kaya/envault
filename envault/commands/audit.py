"""Audit log for vault access and modification events."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

AUDIT_LOG_FILENAME = ".envault_audit.log"


def _audit_log_path(vault_path: Path) -> Path:
    return vault_path.parent / AUDIT_LOG_FILENAME


def record_event(
    vault_path: Path,
    action: str,
    key: Optional[str] = None,
    actor: Optional[str] = None,
    details: Optional[str] = None,
) -> dict:
    """Append a single audit event to the log file next to the vault."""
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "key": key,
        "actor": actor or os.environ.get("USER", "unknown"),
        "details": details,
    }
    log_path = _audit_log_path(vault_path)
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event) + "\n")
    return event


def read_events(vault_path: Path) -> list[dict]:
    """Return all audit events for the given vault, oldest first."""
    log_path = _audit_log_path(vault_path)
    if not log_path.exists():
        return []
    events = []
    with log_path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return events


def clear_log(vault_path: Path) -> int:
    """Delete the audit log. Returns the number of events that were present."""
    log_path = _audit_log_path(vault_path)
    count = len(read_events(vault_path))
    if log_path.exists():
        log_path.unlink()
    return count


def format_events(events: list[dict]) -> str:
    """Return a human-readable summary of audit events."""
    if not events:
        return "No audit events recorded."
    lines = []
    for e in events:
        key_part = f" [{e['key']}]" if e.get("key") else ""
        detail_part = f" — {e['details']}" if e.get("details") else ""
        lines.append(
            f"{e['timestamp']}  {e['actor']:12s}  {e['action']:20s}{key_part}{detail_part}"
        )
    return "\n".join(lines)
