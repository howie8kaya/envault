import pytest
from pathlib import Path
from envault.vault import init_vault, set_secret
from envault.commands.deps import (
    add_dependency, remove_dependency, get_dependencies, get_dependents, DepsError
)

PASS = "testpass"


@pytest.fixture
def vault_path(tmp_path):
    p = tmp_path / "vault.json"
    init_vault(p, PASS)
    set_secret(p, "DB_URL", "postgres://localhost/db", PASS)
    set_secret(p, "DB_POOL", "10", PASS)
    set_secret(p, "API_KEY", "abc123", PASS)
    return p


def test_add_dependency_returns_dep_info(vault_path):
    info = add_dependency(vault_path, "DB_POOL", "DB_URL", PASS)
    assert info.key == "DB_POOL"
    assert "DB_URL" in info.depends_on


def test_add_dependency_idempotent(vault_path):
    add_dependency(vault_path, "DB_POOL", "DB_URL", PASS)
    info = add_dependency(vault_path, "DB_POOL", "DB_URL", PASS)
    assert info.depends_on.count("DB_URL") == 1


def test_add_dependency_missing_key_raises(vault_path):
    with pytest.raises(DepsError):
        add_dependency(vault_path, "MISSING", "DB_URL", PASS)


def test_add_dependency_missing_dep_raises(vault_path):
    with pytest.raises(DepsError):
        add_dependency(vault_path, "DB_POOL", "MISSING", PASS)


def test_get_dependencies_empty_by_default(vault_path):
    info = get_dependencies(vault_path, "DB_URL", PASS)
    assert info.depends_on == []


def test_get_dependencies_after_add(vault_path):
    add_dependency(vault_path, "DB_POOL", "DB_URL", PASS)
    info = get_dependencies(vault_path, "DB_POOL", PASS)
    assert "DB_URL" in info.depends_on


def test_get_dependencies_missing_key_raises(vault_path):
    with pytest.raises(DepsError):
        get_dependencies(vault_path, "NOPE", PASS)


def test_remove_dependency(vault_path):
    add_dependency(vault_path, "DB_POOL", "DB_URL", PASS)
    info = remove_dependency(vault_path, "DB_POOL", "DB_URL", PASS)
    assert "DB_URL" not in info.depends_on


def test_remove_nonexistent_dependency_raises(vault_path):
    with pytest.raises(DepsError):
        remove_dependency(vault_path, "DB_POOL", "DB_URL", PASS)


def test_get_dependents(vault_path):
    add_dependency(vault_path, "DB_POOL", "DB_URL", PASS)
    add_dependency(vault_path, "API_KEY", "DB_URL", PASS)
    dependents = get_dependents(vault_path, "DB_URL", PASS)
    assert "DB_POOL" in dependents
    assert "API_KEY" in dependents


def test_dep_info_str(vault_path):
    add_dependency(vault_path, "DB_POOL", "DB_URL", PASS)
    info = get_dependencies(vault_path, "DB_POOL", PASS)
    assert "DB_POOL" in str(info)
    assert "DB_URL" in str(info)
