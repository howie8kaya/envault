import pytest
from pathlib import Path
from envault.vault import init_vault, set_secret
from envault.commands.group import (
    GroupError, GroupInfo, add_to_group, remove_from_group,
    list_groups, get_group, delete_group
)

PASS = "testpass"


@pytest.fixture
def vault_path(tmp_path):
    p = tmp_path / "test.vault"
    init_vault(p, PASS)
    set_secret(p, PASS, "DB_HOST", "localhost")
    set_secret(p, PASS, "DB_PORT", "5432")
    set_secret(p, PASS, "API_KEY", "secret123")
    return p


def test_add_to_group_returns_group_info(vault_path):
    info = add_to_group(vault_path, PASS, "database", "DB_HOST")
    assert isinstance(info, GroupInfo)
    assert info.name == "database"
    assert "DB_HOST" in info.keys


def test_add_multiple_keys_to_group(vault_path):
    add_to_group(vault_path, PASS, "database", "DB_HOST")
    info = add_to_group(vault_path, PASS, "database", "DB_PORT")
    assert "DB_HOST" in info.keys
    assert "DB_PORT" in info.keys


def test_add_to_group_idempotent(vault_path):
    add_to_group(vault_path, PASS, "database", "DB_HOST")
    info = add_to_group(vault_path, PASS, "database", "DB_HOST")
    assert info.keys.count("DB_HOST") == 1


def test_add_missing_key_raises(vault_path):
    with pytest.raises(GroupError, match="not found"):
        add_to_group(vault_path, PASS, "database", "MISSING_KEY")


def test_remove_from_group(vault_path):
    add_to_group(vault_path, PASS, "database", "DB_HOST")
    add_to_group(vault_path, PASS, "database", "DB_PORT")
    info = remove_from_group(vault_path, PASS, "database", "DB_HOST")
    assert "DB_HOST" not in info.keys
    assert "DB_PORT" in info.keys


def test_remove_from_nonexistent_group_raises(vault_path):
    with pytest.raises(GroupError, match="does not exist"):
        remove_from_group(vault_path, PASS, "ghost", "DB_HOST")


def test_remove_key_not_in_group_raises(vault_path):
    add_to_group(vault_path, PASS, "database", "DB_HOST")
    with pytest.raises(GroupError, match="not in group"):
        remove_from_group(vault_path, PASS, "database", "API_KEY")


def test_list_groups_empty_when_none(vault_path):
    assert list_groups(vault_path, PASS) == []


def test_list_groups_returns_all(vault_path):
    add_to_group(vault_path, PASS, "database", "DB_HOST")
    add_to_group(vault_path, PASS, "api", "API_KEY")
    groups = list_groups(vault_path, PASS)
    names = [g.name for g in groups]
    assert "database" in names
    assert "api" in names


def test_get_group_returns_none_when_missing(vault_path):
    assert get_group(vault_path, PASS, "nope") is None


def test_delete_group(vault_path):
    add_to_group(vault_path, PASS, "database", "DB_HOST")
    delete_group(vault_path, PASS, "database")
    assert get_group(vault_path, PASS, "database") is None


def test_delete_nonexistent_group_raises(vault_path):
    with pytest.raises(GroupError, match="does not exist"):
        delete_group(vault_path, PASS, "ghost")


def test_group_info_str(vault_path):
    add_to_group(vault_path, PASS, "database", "DB_HOST")
    info = get_group(vault_path, PASS, "database")
    assert "database" in str(info)
    assert "DB_HOST" in str(info)
