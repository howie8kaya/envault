import pytest
from pathlib import Path

from envault.vault import init_vault, set_secret
from envault.commands.env_scope import (
    ScopeError,
    ScopeInfo,
    ScopeResult,
    set_scope,
    get_scope,
    remove_scope,
    list_by_scope,
    all_scopes,
)

PASS = "hunter2"


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    p = tmp_path / "test.vault"
    init_vault(str(p), PASS)
    for key, val in [("DB_URL", "postgres://"), ("API_KEY", "abc"), ("CACHE_TTL", "300")]:
        set_secret(str(p), PASS, key, val)
    return p


def test_set_scope_returns_scope_info(vault_path):
    info = set_scope(str(vault_path), PASS, "DB_URL", "backend")
    assert isinstance(info, ScopeInfo)
    assert info.key == "DB_URL"
    assert info.scope == "backend"


def test_scope_info_str(vault_path):
    info = set_scope(str(vault_path), PASS, "API_KEY", "auth")
    assert "API_KEY" in str(info)
    assert "auth" in str(info)


def test_get_scope_returns_assigned_scope(vault_path):
    set_scope(str(vault_path), PASS, "DB_URL", "backend")
    assert get_scope(str(vault_path), PASS, "DB_URL") == "backend"


def test_get_scope_returns_none_when_not_set(vault_path):
    assert get_scope(str(vault_path), PASS, "CACHE_TTL") is None


def test_set_scope_missing_key_raises(vault_path):
    with pytest.raises(ScopeError, match="key not found"):
        set_scope(str(vault_path), PASS, "NONEXISTENT", "infra")


def test_set_scope_empty_scope_raises(vault_path):
    with pytest.raises(ScopeError, match="must not be empty"):
        set_scope(str(vault_path), PASS, "DB_URL", "   ")


def test_remove_scope_returns_true(vault_path):
    set_scope(str(vault_path), PASS, "API_KEY", "auth")
    assert remove_scope(str(vault_path), PASS, "API_KEY") is True


def test_remove_scope_clears_scope(vault_path):
    set_scope(str(vault_path), PASS, "API_KEY", "auth")
    remove_scope(str(vault_path), PASS, "API_KEY")
    assert get_scope(str(vault_path), PASS, "API_KEY") is None


def test_remove_scope_returns_false_when_not_set(vault_path):
    assert remove_scope(str(vault_path), PASS, "CACHE_TTL") is False


def test_list_by_scope_returns_scope_result(vault_path):
    set_scope(str(vault_path), PASS, "DB_URL", "backend")
    set_scope(str(vault_path), PASS, "CACHE_TTL", "backend")
    result = list_by_scope(str(vault_path), PASS, "backend")
    assert isinstance(result, ScopeResult)
    assert set(result.keys) == {"DB_URL", "CACHE_TTL"}


def test_list_by_scope_empty_for_unknown_scope(vault_path):
    result = list_by_scope(str(vault_path), PASS, "nonexistent")
    assert result.keys == []


def test_scope_result_str(vault_path):
    set_scope(str(vault_path), PASS, "API_KEY", "auth")
    result = list_by_scope(str(vault_path), PASS, "auth")
    s = str(result)
    assert "auth" in s
    assert "1 key" in s


def test_all_scopes_returns_grouped_dict(vault_path):
    set_scope(str(vault_path), PASS, "DB_URL", "backend")
    set_scope(str(vault_path), PASS, "API_KEY", "auth")
    set_scope(str(vault_path), PASS, "CACHE_TTL", "backend")
    scopes = all_scopes(str(vault_path), PASS)
    assert set(scopes.keys()) == {"backend", "auth"}
    assert set(scopes["backend"]) == {"DB_URL", "CACHE_TTL"}
    assert scopes["auth"] == ["API_KEY"]


def test_all_scopes_empty_when_none_set(vault_path):
    assert all_scopes(str(vault_path), PASS) == {}
