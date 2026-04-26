"""env_notify.py — Send notifications when secrets change or expire.

Supports simple notification channels: stdout (print), file log, and
optionally a webhook URL (reuses webhook infrastructure).
"""

from __future__ import annotations

import json
import smtplib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path
from typing import List, Optional

from envault.vault import load_vault, VaultError


class NotifyError(Exception):
    """Raised when a notification operation fails."""


@dataclass
class NotifyEvent:
    """A single notification event."""

    vault_path: str
    event_type: str          # "changed", "expired", "expiring_soon", "added", "deleted"
    key: str
    message: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def __str__(self) -> str:
        return f"[{self.timestamp}] {self.event_type.upper()} {self.key}: {self.message}"


@dataclass
class NotifyResult:
    """Result of a notify dispatch."""

    events: List[NotifyEvent]
    channels_used: List[str]
    errors: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        lines = [f"Dispatched {len(self.events)} event(s) via {', '.join(self.channels_used) or 'none'}"]
        if self.errors:
            lines.append(f"  Errors: {'; '.join(self.errors)}")
        return "\n".join(lines)


def _notify_file(events: List[NotifyEvent], log_path: Path) -> None:
    """Append notification events to a log file."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as fh:
        for ev in events:
            fh.write(json.dumps({
                "timestamp": ev.timestamp,
                "vault": ev.vault_path,
                "event_type": ev.event_type,
                "key": ev.key,
                "message": ev.message,
            }) + "\n")


def _notify_email(
    events: List[NotifyEvent],
    smtp_host: str,
    smtp_port: int,
    sender: str,
    recipient: str,
) -> None:
    """Send a summary email for the given events via SMTP (no auth, local relay)."""
    body_lines = ["envault notification summary:\n"]
    for ev in events:
        body_lines.append(str(ev))

    msg = EmailMessage()
    msg["Subject"] = f"envault: {len(events)} secret event(s)"
    msg["From"] = sender
    msg["To"] = recipient
    msg.set_content("\n".join(body_lines))

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=5) as server:
            server.send_message(msg)
    except Exception as exc:  # noqa: BLE001
        raise NotifyError(f"SMTP delivery failed: {exc}") from exc


def notify(
    vault_path: Path,
    passphrase: str,
    events: List[NotifyEvent],
    *,
    log_file: Optional[Path] = None,
    smtp_host: Optional[str] = None,
    smtp_port: int = 25,
    smtp_sender: Optional[str] = None,
    smtp_recipient: Optional[str] = None,
    print_to_stdout: bool = True,
) -> NotifyResult:
    """Dispatch notification events through configured channels.

    Args:
        vault_path:      Path to the vault (used for context only; not modified).
        passphrase:      Vault passphrase (validated before dispatching).
        events:          List of NotifyEvent objects to dispatch.
        log_file:        If set, append events as JSON-lines to this file.
        smtp_host:       If set, send a summary email via this SMTP host.
        smtp_port:       SMTP port (default 25).
        smtp_sender:     Envelope sender address.
        smtp_recipient:  Envelope recipient address.
        print_to_stdout: If True, print each event to stdout.

    Returns:
        NotifyResult summarising what was dispatched.
    """
    # Validate vault is accessible
    try:
        load_vault(vault_path, passphrase)
    except VaultError as exc:
        raise NotifyError(f"Cannot access vault: {exc}") from exc

    if not events:
        return NotifyResult(events=[], channels_used=[])

    channels: List[str] = []
    errors: List[str] = []

    if print_to_stdout:
        channels.append("stdout")
        for ev in events:
            print(str(ev))

    if log_file is not None:
        try:
            _notify_file(events, log_file)
            channels.append("file")
        except OSError as exc:
            errors.append(f"file log failed: {exc}")

    if smtp_host and smtp_sender and smtp_recipient:
        try:
            _notify_email(events, smtp_host, smtp_port, smtp_sender, smtp_recipient)
            channels.append("email")
        except NotifyError as exc:
            errors.append(str(exc))

    return NotifyResult(events=events, channels_used=channels, errors=errors)


def build_expiry_events(
    vault_path: Path,
    passphrase: str,
    *,
    warn_days: int = 7,
) -> List[NotifyEvent]:
    """Scan the vault's expiry metadata and return events for expired/expiring keys.

    Requires envault.commands.expire to be available; silently returns [] otherwise.
    """
    try:
        from envault.commands.expire import get_expiry, ExpiryInfo  # noqa: PLC0415
    except ImportError:
        return []

    try:
        data = load_vault(vault_path, passphrase)
    except VaultError:
        return []

    events: List[NotifyEvent] = []
    now = datetime.now(timezone.utc)

    for key in data.get("secrets", {}):
        info: Optional[ExpiryInfo] = get_expiry(vault_path, passphrase, key)
        if info is None:
            continue
        delta = info.expires_at - now
        days_left = delta.total_seconds() / 86400
        if days_left <= 0:
            events.append(NotifyEvent(
                vault_path=str(vault_path),
                event_type="expired",
                key=key,
                message=f"Secret expired at {info.expires_at.isoformat()}",
            ))
        elif days_left <= warn_days:
            events.append(NotifyEvent(
                vault_path=str(vault_path),
                event_type="expiring_soon",
                key=key,
                message=f"Expires in {days_left:.1f} day(s) ({info.expires_at.isoformat()})",
            ))

    return events
