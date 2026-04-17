import pytest
from pathlib import Path
from envault.vault import init_vault, set_secret
from envault.commands.alias import (
    AliasError,
    AliasInfo,
    set_alias,
    remove_alias,
    resolve_alias,
    list_aliases,
)

PASS = "testpass"


@pytest.fixture
def vault_path(tmp_path):
    p = tmp_path / "test.vault"
    init_vault(p, PASS)
    set_secret(p, "DATABASE_URL", "postgres://localhost/db", PASS)
    set_secret(p, "API_KEY", "secret123", PASS)
    return p


def test_set_alias_returns_alias_info(vault_path):
    info = set_alias(vault_path, "db", "DATABASE_URL", PASS)
    assert isinstance(info, AliasInfo)
    assert info.alias == "db"
    assert info.key == "DATABASE_URL"


def test_alias_str(vault_path):
    info = set_alias(vault_path, "db", "DATABASE_URL", PASS)
    assert str(info) == "db -> DATABASE_URL"


def test_resolve_alias_returns_correct_key(vault_path):
    set_alias(vault_path, "db", "DATABASE_URL", PASS)
    info = resolve_alias(vault_path, "db", PASS)
    assert info.key == "DATABASE_URL"


def test_set_alias_missing_key_raises(vault_path):
    with pytest.raises(AliasError, match="not found"):
        set_alias(vault_path, "ghost", "NONEXISTENT", PASS)


def test_set_alias_invalid_identifier_raises(vault_path):
    with pytest.raises(AliasError, match="valid identifier"):
        set_alias(vault_path, "my-alias!", "DATABASE_URL", PASS)


def test_remove_alias(vault_path):
    set_alias(vault_path, "db", "DATABASE_URL", PASS)
    remove_alias(vault_path, "db", PASS)
    with pytest.raises(AliasError):
        resolve_alias(vault_path, "db", PASS)


def test_remove_alias_missing_raises(vault_path):
    with pytest.raises(AliasError, match="does not exist"):
        remove_alias(vault_path, "nope", PASS)


def test_list_aliases_empty_when_none(vault_path):
    assert list_aliases(vault_path, PASS) == []


def test_list_aliases_returns_all(vault_path):
    set_alias(vault_path, "db", "DATABASE_URL", PASS)
    set_alias(vault_path, "api", "API_KEY", PASS)
    aliases = list_aliases(vault_path, PASS)
    assert len(aliases) == 2
    names = {a.alias for a in aliases}
    assert names == {"db", "api"}


def test_set_alias_overwrites_existing(vault_path):
    set_alias(vault_path, "key", "DATABASE_URL", PASS)
    set_alias(vault_path, "key", "API_KEY", PASS)
    info = resolve_alias(vault_path, "key", PASS)
    assert info.key == "API_KEY"
