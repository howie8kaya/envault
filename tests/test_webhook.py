"""Tests for envault.commands.webhook."""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from envault.vault import init_vault
from envault.commands.webhook import (
    WebhookError, WebhookInfo, register_webhook, unregister_webhook,
    list_webhooks, fire_webhook, notify,
)

PASS = "test-pass"


@pytest.fixture
def vault_path(tmp_path):
    p = tmp_path / "vault.env"
    init_vault(p, PASS)
    return p


def test_register_webhook_returns_info(vault_path):
    info = register_webhook(vault_path, PASS, "https://example.com/hook", ["set", "delete"])
    assert isinstance(info, WebhookInfo)
    assert info.url == "https://example.com/hook"
    assert "set" in info.events
    assert "delete" in info.events


def test_register_webhook_idempotent(vault_path):
    register_webhook(vault_path, PASS, "https://example.com/hook", ["set"])
    info = register_webhook(vault_path, PASS, "https://example.com/hook", ["set"])
    assert info.events.count("set") == 1


def test_register_webhook_invalid_url_raises(vault_path):
    with pytest.raises(WebhookError, match="Invalid URL"):
        register_webhook(vault_path, PASS, "ftp://bad.url", ["set"])


def test_register_webhook_no_events_raises(vault_path):
    with pytest.raises(WebhookError, match="event type"):
        register_webhook(vault_path, PASS, "https://example.com/hook", [])


def test_list_webhooks_empty_when_none(vault_path):
    assert list_webhooks(vault_path, PASS) == []


def test_list_webhooks_returns_registered(vault_path):
    register_webhook(vault_path, PASS, "https://a.com", ["set"])
    register_webhook(vault_path, PASS, "https://b.com", ["delete"])
    hooks = list_webhooks(vault_path, PASS)
    urls = [h.url for h in hooks]
    assert "https://a.com" in urls
    assert "https://b.com" in urls


def test_unregister_webhook_returns_true(vault_path):
    register_webhook(vault_path, PASS, "https://a.com", ["set"])
    assert unregister_webhook(vault_path, PASS, "https://a.com") is True
    assert list_webhooks(vault_path, PASS) == []


def test_unregister_missing_returns_false(vault_path):
    assert unregister_webhook(vault_path, PASS, "https://missing.com") is False


def test_webhook_info_str():
    info = WebhookInfo(url="https://x.com", events=["set"])
    assert "https://x.com" in str(info)


def test_notify_fires_matching_hooks(vault_path):
    register_webhook(vault_path, PASS, "https://hook.io", ["set"])
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    with patch("urllib.request.urlopen", return_value=mock_resp):
        results = notify(vault_path, PASS, "set", {"key": "FOO"})
    assert len(results) == 1
    assert results[0]["status"] == 200


def test_notify_skips_non_matching_events(vault_path):
    register_webhook(vault_path, PASS, "https://hook.io", ["delete"])
    results = notify(vault_path, PASS, "set", {"key": "FOO"})
    assert results == []
