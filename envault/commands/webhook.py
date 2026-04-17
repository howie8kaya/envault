"""Webhook notification support for vault events."""
from __future__ import annotations
import json
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional
from envault.vault import load_vault, save_vault, VaultError


class WebhookError(Exception):
    pass


@dataclass
class WebhookInfo:
    url: str
    events: List[str]

    def __str__(self) -> str:
        return f"WebhookInfo(url={self.url!r}, events={self.events})"


def _webhooks_meta(vault: dict) -> dict:
    return vault.setdefault("__meta__", {}).setdefault("webhooks", {})


def register_webhook(vault_path: Path, passphrase: str, url: str, events: List[str]) -> WebhookInfo:
    """Register a webhook URL for the given event types."""
    if not url.startswith(("http://", "https://")):
        raise WebhookError(f"Invalid URL: {url!r}")
    if not events:
        raise WebhookError("At least one event type must be specified.")
    vault = load_vault(vault_path, passphrase)
    meta = _webhooks_meta(vault)
    entry = meta.get(url, {"url": url, "events": []})
    for ev in events:
        if ev not in entry["events"]:
            entry["events"].append(ev)
    meta[url] = entry
    save_vault(vault_path, passphrase, vault)
    return WebhookInfo(url=url, events=entry["events"])


def unregister_webhook(vault_path: Path, passphrase: str, url: str) -> bool:
    """Remove a registered webhook. Returns True if it existed."""
    vault = load_vault(vault_path, passphrase)
    meta = _webhooks_meta(vault)
    if url not in meta:
        return False
    del meta[url]
    save_vault(vault_path, passphrase, vault)
    return True


def list_webhooks(vault_path: Path, passphrase: str) -> List[WebhookInfo]:
    """Return all registered webhooks."""
    vault = load_vault(vault_path, passphrase)
    meta = _webhooks_meta(vault)
    return [WebhookInfo(url=v["url"], events=v["events"]) for v in meta.values()]


def fire_webhook(url: str, payload: dict, timeout: int = 5) -> int:
    """POST payload as JSON to url. Returns HTTP status code."""
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status
    except urllib.error.HTTPError as exc:
        return exc.code
    except Exception as exc:
        raise WebhookError(f"Failed to fire webhook: {exc}") from exc


def notify(vault_path: Path, passphrase: str, event: str, payload: dict) -> List[dict]:
    """Fire all webhooks registered for the given event. Returns list of result dicts."""
    results = []
    for wh in list_webhooks(vault_path, passphrase):
        if event in wh.events:
            try:
                status = fire_webhook(wh.url, {"event": event, **payload})
                results.append({"url": wh.url, "status": status, "error": None})
            except WebhookError as exc:
                results.append({"url": wh.url, "status": None, "error": str(exc)})
    return results
