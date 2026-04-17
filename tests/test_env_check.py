import os
import pytest
from envault.vault import init_vault, set_secret
from envault.commands.env_check import (
    check_env, missing_keys, format_check_results, EnvCheckError
)


@pytest.fixture
def vault_path(tmp_path):
    p = tmp_path / "vault.env"
    init_vault(str(p), "pass")
    set_secret(str(p), "pass", "DB_URL", "postgres://localhost/db")
    set_secret(str(p), "pass", "API_KEY", "secret123")
    set_secret(str(p), "pass", "DEBUG", "true")
    return str(p)


def test_check_all_missing(vault_path, monkeypatch):
    monkeypatch.delenv("DB_URL", raising=False)
    monkeypatch.delenv("API_KEY", raising=False)
    monkeypatch.delenv("DEBUG", raising=False)
    results = check_env(vault_path, "pass")
    assert all(not r.found for r in results)
    assert len(results) == 3


def test_check_some_present(vault_path, monkeypatch):
    monkeypatch.setenv("DB_URL", "postgres://localhost/db")
    monkeypatch.delenv("API_KEY", raising=False)
    results = check_env(vault_path, "pass", keys=["DB_URL", "API_KEY"])
    found = {r.key: r.found for r in results}
    assert found["DB_URL"] is True
    assert found["API_KEY"] is False


def test_check_env_value_captured(vault_path, monkeypatch):
    monkeypatch.setenv("DEBUG", "1")
    results = check_env(vault_path, "pass", keys=["DEBUG"])
    assert results[0].env_value == "1"


def test_missing_keys_helper(vault_path, monkeypatch):
    monkeypatch.setenv("DB_URL", "x")
    monkeypatch.delenv("API_KEY", raising=False)
    monkeypatch.delenv("DEBUG", raising=False)
    results = check_env(vault_path, "pass")
    missing = missing_keys(results)
    assert "API_KEY" in missing
    assert "DEBUG" in missing
    assert "DB_URL" not in missing


def test_check_wrong_passphrase_raises(vault_path):
    with pytest.raises(EnvCheckError):
        check_env(vault_path, "wrongpass")


def test_check_unknown_key_raises(vault_path):
    with pytest.raises(EnvCheckError, match="not found in vault"):
        check_env(vault_path, "pass", keys=["NONEXISTENT"])


def test_format_check_results(vault_path, monkeypatch):
    monkeypatch.setenv("DB_URL", "x")
    monkeypatch.delenv("API_KEY", raising=False)
    results = check_env(vault_path, "pass", keys=["DB_URL", "API_KEY"])
    output = format_check_results(results)
    assert "[OK] DB_URL" in output
    assert "[MISSING] API_KEY" in output
    assert "1/2 keys present" in output


def test_check_result_str_ok(vault_path, monkeypatch):
    monkeypatch.setenv("DB_URL", "x")
    results = check_env(vault_path, "pass", keys=["DB_URL"])
    assert str(results[0]) == "[OK] DB_URL"
