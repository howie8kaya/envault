"""Tests for envault.commands.watch."""

import time
from pathlib import Path

import pytest

from envault.commands.watch import (
    WatchError,
    WatchEvent,
    watch_env_file,
    _sync_changes,
)
from envault.vault import init_vault, load_vault, set_secret, save_vault, get_secret

PASS = "hunter2"


@pytest.fixture
def vault_path(tmp_path):
    p = tmp_path / "test.vault"
    init_vault(p, PASS)
    return p


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("KEY1=hello\nKEY2=world\n")
    return p


def test_sync_changes_detects_new_key(vault_path, env_file):
    prev = {"KEY1": "hello"}
    changed, new_env = _sync_changes(env_file, vault_path, PASS, prev)
    assert "KEY1" in changed or "KEY2" in changed
    assert new_env["KEY1"] == "hello"
    assert new_env["KEY2"] == "world"


def test_sync_changes_writes_to_vault(vault_path, env_file):
    _sync_changes(env_file, vault_path, PASS, {})
    vault = load_vault(vault_path, PASS)
    assert get_secret(vault, "KEY1", PASS) == "hello"
    assert get_secret(vault, "KEY2", PASS) == "world"


def test_sync_no_changes_when_identical(vault_path, env_file):
    prev = {"KEY1": "hello", "KEY2": "world"}
    changed, _ = _sync_changes(env_file, vault_path, PASS, prev)
    assert changed == []


def test_watch_raises_if_env_missing(vault_path, tmp_path):
    with pytest.raises(WatchError, match="File not found"):
        watch_env_file(tmp_path / "missing.env", vault_path, PASS, max_iterations=0)


def test_watch_raises_if_vault_missing(env_file, tmp_path):
    with pytest.raises(WatchError, match="Vault not found"):
        watch_env_file(env_file, tmp_path / "missing.vault", PASS, max_iterations=0)


def test_watch_calls_on_change_callback(vault_path, tmp_path):
    env = tmp_path / ".env"
    env.write_text("A=1\n")
    events = []

    def _write_and_wait():
        time.sleep(0.05)
        env.write_text("A=2\n")

    import threading
    t = threading.Thread(target=_write_and_wait)
    t.start()
    watch_env_file(
        env, vault_path, PASS,
        interval=0.02,
        on_change=events.append,
        max_iterations=10,
    )
    t.join()
    assert any("A" in e.changed_keys for e in events)


def test_watch_event_str():
    e = WatchEvent(path=Path(".env"), changed_keys=["FOO", "BAR"])
    assert ".env" in str(e)
    assert "FOO" in str(e)
