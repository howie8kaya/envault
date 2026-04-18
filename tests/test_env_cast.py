import pytest
from pathlib import Path
from envault.vault import init_vault, set_secret
from envault.commands.env_cast import cast_secret, cast_all, CastError, CastResult

PASS = "testpass"


@pytest.fixture
def vault_path(tmp_path):
    p = tmp_path / "test.vault"
    init_vault(str(p), PASS)
    set_secret(str(p), PASS, "COUNT", "42")
    set_secret(str(p), PASS, "RATIO", "3.14")
    set_secret(str(p), PASS, "ENABLED", "true")
    set_secret(str(p), PASS, "TAGS", "a, b, c")
    set_secret(str(p), PASS, "NAME", "hello")
    return str(p)


def test_cast_int(vault_path):
    result = cast_secret(vault_path, PASS, "COUNT", "int")
    assert result.value == 42
    assert result.cast_type == "int"


def test_cast_float(vault_path):
    result = cast_secret(vault_path, PASS, "RATIO", "float")
    assert abs(result.value - 3.14) < 0.001


def test_cast_bool_true(vault_path):
    result = cast_secret(vault_path, PASS, "ENABLED", "bool")
    assert result.value is True


def test_cast_list(vault_path):
    result = cast_secret(vault_path, PASS, "TAGS", "list")
    assert result.value == ["a", "b", "c"]


def test_cast_str(vault_path):
    result = cast_secret(vault_path, PASS, "NAME", "str")
    assert result.value == "hello"


def test_cast_result_str(vault_path):
    result = cast_secret(vault_path, PASS, "COUNT", "int")
    assert "COUNT" in str(result)
    assert "int" in str(result)


def test_cast_missing_key_raises(vault_path):
    with pytest.raises(CastError, match="not found"):
        cast_secret(vault_path, PASS, "MISSING", "int")


def test_cast_invalid_type_raises(vault_path):
    with pytest.raises(CastError, match="Unsupported"):
        cast_secret(vault_path, PASS, "COUNT", "bytes")


def test_cast_bad_int_raises(vault_path):
    set_secret(vault_path, PASS, "BAD", "notanumber")
    with pytest.raises(CastError, match="Cannot cast"):
        cast_secret(vault_path, PASS, "BAD", "int")


def test_cast_bad_bool_raises(vault_path):
    set_secret(vault_path, PASS, "WEIRD", "maybe")
    with pytest.raises(CastError, match="Cannot cast"):
        cast_secret(vault_path, PASS, "WEIRD", "bool")


def test_cast_all(vault_path):
    results = cast_all(vault_path, PASS, {"COUNT": "int", "ENABLED": "bool"})
    assert len(results) == 2
    values = {r.key: r.value for r in results}
    assert values["COUNT"] == 42
    assert values["ENABLED"] is True
