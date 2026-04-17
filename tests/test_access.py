import json
import pytest
from pathlib import Path

from envault.vault import init_vault, set_secret
from envault.commands.access import (
    AccessError,
    set_access,
    get_access,
    revoke_access,
    list_roles,
    filter_by_role,
)

PASS = "hunter2"


@pytest.fixture
def vault_path(tmp_path):
    p = tmp_path / "test.vault"
    init_vault(p, PASS)
    set_secret(p, "DB_URL", "postgres://localhost/db", PASS)
    set_secret(p, "API_KEY", "secret-api", PASS)
    set_secret(p, "REDIS_URL", "redis://localhost", PASS)
    return p


def test_set_access_returns_full_meta(vault_path):
    meta = set_access(vault_path, "backend", ["DB_URL", "REDIS_URL"])
    assert "backend" in meta
    assert meta["backend"] == ["DB_URL", "REDIS_URL"]


def test_get_access_returns_keys(vault_path):
    set_access(vault_path, "frontend", ["API_KEY"])
    keys = get_access(vault_path, "frontend")
    assert keys == ["API_KEY"]


def test_get_access_returns_none_for_unknown_role(vault_path):
    assert get_access(vault_path, "ghost") is None


def test_set_access_missing_key_raises(vault_path):
    with pytest.raises(AccessError, match="Key not found"):
        set_access(vault_path, "ops", ["NONEXISTENT"])


def test_revoke_access_removes_role(vault_path):
    set_access(vault_path, "backend", ["DB_URL"])
    existed = revoke_access(vault_path, "backend")
    assert existed is True
    assert get_access(vault_path, "backend") is None


def test_revoke_access_returns_false_when_not_set(vault_path):
    assert revoke_access(vault_path, "nobody") is False


def test_list_roles_empty_when_no_rules(vault_path):
    assert list_roles(vault_path) == []


def test_list_roles_returns_all(vault_path):
    set_access(vault_path, "backend", ["DB_URL"])
    set_access(vault_path, "frontend", ["API_KEY"])
    roles = list_roles(vault_path)
    assert set(roles) == {"backend", "frontend"}


def test_filter_by_role_returns_decrypted_secrets(vault_path):
    set_access(vault_path, "backend", ["DB_URL", "REDIS_URL"])
    secrets = filter_by_role(vault_path, PASS, "backend")
    assert secrets["DB_URL"] == "postgres://localhost/db"
    assert secrets["REDIS_URL"] == "redis://localhost"
    assert "API_KEY" not in secrets


def test_filter_by_role_no_rules_raises(vault_path):
    with pytest.raises(AccessError, match="No access rules"):
        filter_by_role(vault_path, PASS, "unknown")
