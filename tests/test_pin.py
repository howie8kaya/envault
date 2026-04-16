import pytest
from pathlib import Path
from envault.vault import init_vault, set_secret
from envault.commands.pin import (
    pin_secret, unpin_secret, is_pinned, list_pins, PinError
)

PASS = "testpass"


@pytest.fixture
def vault_path(tmp_path):
    p = tmp_path / "vault.env"
    init_vault(p, PASS)
    set_secret(p, PASS, "API_KEY", "abc123")
    set_secret(p, PASS, "DB_PASS", "secret")
    return p


def test_pin_secret_returns_pin_info(vault_path):
    info = pin_secret(vault_path, PASS, "API_KEY")
    assert info.key == "API_KEY"
    assert info.pinned is True


def test_is_pinned_true_after_pin(vault_path):
    pin_secret(vault_path, PASS, "API_KEY")
    assert is_pinned(vault_path, PASS, "API_KEY") is True


def test_is_pinned_false_by_default(vault_path):
    assert is_pinned(vault_path, PASS, "DB_PASS") is False


def test_unpin_secret(vault_path):
    pin_secret(vault_path, PASS, "API_KEY")
    info = unpin_secret(vault_path, PASS, "API_KEY")
    assert info.pinned is False
    assert is_pinned(vault_path, PASS, "API_KEY") is False


def test_unpin_nonexistent_pin_is_safe(vault_path):
    info = unpin_secret(vault_path, PASS, "DB_PASS")
    assert info.pinned is False


def test_pin_missing_key_raises(vault_path):
    with pytest.raises(PinError, match="Key not found"):
        pin_secret(vault_path, PASS, "GHOST_KEY")


def test_list_pins_returns_all_secrets(vault_path):
    pin_secret(vault_path, PASS, "API_KEY")
    results = list_pins(vault_path, PASS)
    keys = {r.key for r in results}
    assert "API_KEY" in keys
    assert "DB_PASS" in keys


def test_list_pins_reflects_pin_status(vault_path):
    pin_secret(vault_path, PASS, "API_KEY")
    results = {r.key: r.pinned for r in list_pins(vault_path, PASS)}
    assert results["API_KEY"] is True
    assert results["DB_PASS"] is False


def test_pin_info_str(vault_path):
    info = pin_secret(vault_path, PASS, "API_KEY")
    assert str(info) == "API_KEY: pinned"
