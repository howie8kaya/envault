"""Tests for envault.commands.env_clone."""

import pytest
from pathlib import Path

from envault.vault import init_vault, set_secret, get_secret, VaultError
from envault.commands.env_clone import CloneError, CloneResult, clone_vault, list_clone_candidates


@pytest.fixture
def src_vault(tmp_path):
    p = tmp_path / "src.vault"
    init_vault(p, "srcpass")
    set_secret(p, "srcpass", "APP_KEY", "abc123")
    set_secret(p, "srcpass", "APP_SECRET", "xyz789")
    set_secret(p, "srcpass", "DB_URL", "postgres://localhost/db")
    return p


@pytest.fixture
def dst_path(tmp_path):
    return tmp_path / "dst.vault"


def test_clone_returns_result(src_vault, dst_path):
    result = clone_vault(src_vault, dst_path, "srcpass", "dstpass")
    assert isinstance(result, CloneResult)


def test_clone_copies_all_keys(src_vault, dst_path):
    result = clone_vault(src_vault, dst_path, "srcpass", "dstpass")
    assert set(result.keys_copied) == {"APP_KEY", "APP_SECRET", "DB_URL"}
    assert result.keys_skipped == []


def test_clone_values_readable_with_new_passphrase(src_vault, dst_path):
    clone_vault(src_vault, dst_path, "srcpass", "dstpass")
    assert get_secret(dst_path, "dstpass", "APP_KEY") == "abc123"
    assert get_secret(dst_path, "dstpass", "DB_URL") == "postgres://localhost/db"


def test_clone_with_prefix_filters_keys(src_vault, dst_path):
    result = clone_vault(src_vault, dst_path, "srcpass", "dstpass", prefix="APP_")
    assert set(result.keys_copied) == {"APP_KEY", "APP_SECRET"}
    assert "DB_URL" in result.keys_skipped


def test_clone_prefix_values_readable(src_vault, dst_path):
    clone_vault(src_vault, dst_path, "srcpass", "dstpass", prefix="APP_")
    assert get_secret(dst_path, "dstpass", "APP_SECRET") == "xyz789"
    with pytest.raises(VaultError):
        get_secret(dst_path, "dstpass", "DB_URL")


def test_clone_missing_source_raises(dst_path, tmp_path):
    missing = tmp_path / "nope.vault"
    with pytest.raises(CloneError, match="Source vault not found"):
        clone_vault(missing, dst_path, "pass", "pass")


def test_clone_no_overwrite_raises_if_dst_exists(src_vault, dst_path):
    clone_vault(src_vault, dst_path, "srcpass", "dstpass")
    with pytest.raises(Exception):
        clone_vault(src_vault, dst_path, "srcpass", "dstpass", overwrite=False)


def test_clone_overwrite_succeeds(src_vault, dst_path):
    clone_vault(src_vault, dst_path, "srcpass", "dstpass")
    result = clone_vault(src_vault, dst_path, "srcpass", "newpass", overwrite=True)
    assert len(result.keys_copied) == 3


def test_clone_result_str(src_vault, dst_path):
    result = clone_vault(src_vault, dst_path, "srcpass", "dstpass")
    s = str(result)
    assert "Cloned" in s
    assert "3" in s


def test_list_clone_candidates_no_prefix(src_vault):
    candidates = list_clone_candidates(src_vault, "srcpass")
    assert candidates == sorted(["APP_KEY", "APP_SECRET", "DB_URL"])


def test_list_clone_candidates_with_prefix(src_vault):
    candidates = list_clone_candidates(src_vault, "srcpass", prefix="APP_")
    assert "DB_URL" not in candidates
    assert "APP_KEY" in candidates
