import pytest
from pathlib import Path
from envault.vault import init_vault, set_secret
from envault.commands.env_mask import mask_secrets, format_masked, MaskError, _mask_value


@pytest.fixture
def vault_path(tmp_path):
    p = tmp_path / "test.vault"
    init_vault(str(p), "pass")
    set_secret(str(p), "pass", "DB_PASSWORD", "supersecret")
    set_secret(str(p), "pass", "API_KEY", "abc123xyz")
    set_secret(str(p), "pass", "EMPTY_VAL", "")
    return str(p)


def test_mask_value_fully_masked():
    assert _mask_value("hello") == "*****"


def test_mask_value_reveal_chars():
    assert _mask_value("hello", reveal=2) == "he***"


def test_mask_value_reveal_exceeds_length():
    assert _mask_value("hi", reveal=10) == "hi"


def test_mask_value_empty():
    assert _mask_value("") == ""


def test_mask_secrets_all_keys(vault_path):
    entries = mask_secrets(vault_path, "pass")
    keys = [e.key for e in entries]
    assert "DB_PASSWORD" in keys
    assert "API_KEY" in keys


def test_mask_secrets_values_hidden(vault_path):
    entries = mask_secrets(vault_path, "pass")
    by_key = {e.key: e for e in entries}
    assert by_key["DB_PASSWORD"].masked == "*" * len("supersecret")
    assert "supersecret" not in by_key["DB_PASSWORD"].masked


def test_mask_secrets_length_correct(vault_path):
    entries = mask_secrets(vault_path, "pass")
    by_key = {e.key: e for e in entries}
    assert by_key["API_KEY"].length == len("abc123xyz")


def test_mask_secrets_selective_keys(vault_path):
    entries = mask_secrets(vault_path, "pass", keys=["API_KEY"])
    assert len(entries) == 1
    assert entries[0].key == "API_KEY"


def test_mask_secrets_with_reveal(vault_path):
    entries = mask_secrets(vault_path, "pass", keys=["API_KEY"], reveal=3)
    assert entries[0].masked.startswith("abc")
    assert "*" in entries[0].masked


def test_mask_secrets_missing_key_raises(vault_path):
    with pytest.raises(MaskError, match="NOPE"):
        mask_secrets(vault_path, "pass", keys=["NOPE"])


def test_masked_entry_str(vault_path):
    entries = mask_secrets(vault_path, "pass", keys=["DB_PASSWORD"])
    s = str(entries[0])
    assert "DB_PASSWORD" in s
    assert "chars" in s


def test_format_masked_empty():
    assert format_masked([]) == "(no secrets)"


def test_format_masked_multiple(vault_path):
    entries = mask_secrets(vault_path, "pass", keys=["DB_PASSWORD", "API_KEY"])
    output = format_masked(entries)
    assert "DB_PASSWORD" in output
    assert "API_KEY" in output
