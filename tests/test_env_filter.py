import pytest
import os
from envault.vault import init_vault, set_secret
from envault.commands.env_filter import filter_vault, extract_filtered, FilterError
from envault.crypto import decrypt
from envault.vault import load_vault


@pytest.fixture
def vault_path(tmp_path):
    p = str(tmp_path / "test.vault")
    init_vault(p, "pass")
    set_secret(p, "pass", "DB_HOST", "localhost")
    set_secret(p, "pass", "DB_PORT", "5432")
    set_secret(p, "pass", "APP_SECRET", "abc123")
    set_secret(p, "pass", "APP_DEBUG", "true")
    set_secret(p, "pass", "REDIS_URL", "redis://localhost")
    return p


def test_filter_by_prefix(vault_path):
    result = filter_vault(vault_path, "pass", prefix="DB_")
    assert set(result.matched) == {"DB_HOST", "DB_PORT"}


def test_filter_by_suffix(vault_path):
    result = filter_vault(vault_path, "pass", suffix="_URL")
    assert result.matched == ["REDIS_URL"]


def test_filter_by_pattern(vault_path):
    result = filter_vault(vault_path, "pass", pattern="APP_*")
    assert set(result.matched) == {"APP_SECRET", "APP_DEBUG"}


def test_filter_total_count(vault_path):
    result = filter_vault(vault_path, "pass", prefix="DB_")
    assert result.total == 5


def test_filter_no_criteria_raises(vault_path):
    with pytest.raises(FilterError):
        filter_vault(vault_path, "pass")


def test_filter_invert(vault_path):
    result = filter_vault(vault_path, "pass", prefix="DB_", invert=True)
    assert "DB_HOST" not in result.matched
    assert "APP_SECRET" in result.matched


def test_filter_no_matches(vault_path):
    result = filter_vault(vault_path, "pass", prefix="NOPE_")
    assert result.matched == []


def test_filter_result_str(vault_path):
    result = filter_vault(vault_path, "pass", prefix="DB_")
    assert "2/5" in str(result)


def test_extract_filtered_creates_dest(vault_path, tmp_path):
    dest = str(tmp_path / "dest.vault")
    result = extract_filtered(vault_path, "pass", dest, "newpass", prefix="DB_")
    assert len(result.matched) == 2
    dst = load_vault(dest)
    assert "DB_HOST" in dst["secrets"]


def test_extract_filtered_values_readable(vault_path, tmp_path):
    dest = str(tmp_path / "dest.vault")
    extract_filtered(vault_path, "pass", dest, "newpass", prefix="APP_")
    dst = load_vault(dest)
    val = decrypt(dst["secrets"]["APP_DEBUG"], "newpass")
    assert val == "true"
