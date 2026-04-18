import pytest
from pathlib import Path
from envault.vault import init_vault, set_secret
from envault.commands.env_redact import redact_text, redact_file, RedactError

PASS = "hunter2"


@pytest.fixture
def vault_path(tmp_path):
    p = tmp_path / "test.vault"
    init_vault(str(p), PASS)
    set_secret(str(p), PASS, "API_KEY", "supersecret123")
    set_secret(str(p), PASS, "DB_PASS", "dbpassword!")
    set_secret(str(p), PASS, "SHORT", "ab")
    return str(p)


def test_redact_replaces_secret_value(vault_path):
    result = redact_text("my key is supersecret123 ok", vault_path, PASS)
    assert "supersecret123" not in result.redacted
    assert "[REDACTED]" in result.redacted


def test_redact_replaced_list_contains_key(vault_path):
    result = redact_text("token=supersecret123", vault_path, PASS)
    assert "API_KEY" in result.replaced


def test_redact_multiple_secrets(vault_path):
    text = "api=supersecret123 db=dbpassword!"
    result = redact_text(text, vault_path, PASS)
    assert "supersecret123" not in result.redacted
    assert "dbpassword!" not in result.redacted
    assert len(result.replaced) == 2


def test_redact_no_match_returns_original(vault_path):
    result = redact_text("nothing sensitive here", vault_path, PASS)
    assert result.redacted == "nothing sensitive here"
    assert result.replaced == []


def test_redact_short_values_skipped(vault_path):
    result = redact_text("value is ab end", vault_path, PASS)
    assert "ab" in result.redacted
    assert "SHORT" not in result.replaced


def test_redact_custom_placeholder(vault_path):
    result = redact_text("supersecret123", vault_path, PASS, placeholder="***")
    assert result.redacted == "***"


def test_redact_result_str(vault_path):
    result = redact_text("supersecret123", vault_path, PASS)
    s = str(result)
    assert "1" in s
    assert "API_KEY" in s


def test_redact_file(vault_path, tmp_path):
    f = tmp_path / "log.txt"
    f.write_text("token supersecret123 end")
    result = redact_file(str(f), vault_path, PASS)
    assert "supersecret123" not in result.redacted
    # original file unchanged
    assert "supersecret123" in f.read_text()


def test_redact_file_write(vault_path, tmp_path):
    f = tmp_path / "log.txt"
    f.write_text("token supersecret123 end")
    redact_file(str(f), vault_path, PASS, write=True)
    assert "supersecret123" not in f.read_text()
    assert "[REDACTED]" in f.read_text()


def test_redact_file_missing_raises(vault_path):
    with pytest.raises(RedactError):
        redact_file("/nonexistent/file.txt", vault_path, PASS)
