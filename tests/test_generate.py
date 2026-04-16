import pytest
from pathlib import Path

from envault.vault import init_vault, load_vault, set_secret
from envault.commands.generate import generate_secret, list_charsets, GenerateError


@pytest.fixture
def vault_path(tmp_path):
    p = tmp_path / "test.vault"
    init_vault(p, "pass123")
    return p


def test_generate_returns_result(vault_path):
    result = generate_secret(vault_path, "pass123", "MY_KEY")
    assert result.key == "MY_KEY"
    assert len(result.value) == 32
    assert result.charset == "alphanumeric"


def test_generate_stores_in_vault(vault_path):
    result = generate_secret(vault_path, "pass123", "API_KEY", length=16)
    vault = load_vault(vault_path, "pass123")
    assert vault["API_KEY"] == result.value


def test_generate_custom_length(vault_path):
    result = generate_secret(vault_path, "pass123", "TOKEN", length=64)
    assert len(result.value) == 64


def test_generate_hex_charset(vault_path):
    result = generate_secret(vault_path, "pass123", "HEX_KEY", length=20, charset="hex")
    assert all(c in "0123456789abcdef" for c in result.value)


def test_generate_numeric_charset(vault_path):
    result = generate_secret(vault_path, "pass123", "PIN", length=6, charset="numeric")
    assert result.value.isdigit()


def test_generate_raises_if_key_exists(vault_path):
    set_secret(vault_path, "pass123", "EXISTING", "oldval")
    with pytest.raises(GenerateError, match="already exists"):
        generate_secret(vault_path, "pass123", "EXISTING")


def test_generate_overwrite_replaces_value(vault_path):
    set_secret(vault_path, "pass123", "EXISTING", "oldval")
    result = generate_secret(vault_path, "pass123", "EXISTING", overwrite=True)
    vault = load_vault(vault_path, "pass123")
    assert vault["EXISTING"] == result.value
    assert vault["EXISTING"] != "oldval"


def test_generate_invalid_charset_raises(vault_path):
    with pytest.raises(GenerateError, match="Unknown charset"):
        generate_secret(vault_path, "pass123", "KEY", charset="binary")


def test_generate_zero_length_raises(vault_path):
    with pytest.raises(GenerateError, match="Length must be at least 1"):
        generate_secret(vault_path, "pass123", "KEY", length=0)


def test_list_charsets_returns_expected(vault_path):
    charsets = list_charsets()
    assert "alphanumeric" in charsets
    assert "hex" in charsets
    assert "full" in charsets


def test_generate_str_representation(vault_path):
    result = generate_secret(vault_path, "pass123", "SECRET", length=12)
    s = str(result)
    assert "SECRET" in s
    assert "12" in s
    assert result.value not in s
