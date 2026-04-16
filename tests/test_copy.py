"""Tests for envault.commands.copy."""
import pytest
from pathlib import Path
from envault.vault import init_vault, set_secret, get_secret
from envault.commands.copy import copy_secrets, list_copy_candidates, CopyError


@pytest.fixture
def src_vault(tmp_path):
    p = str(tmp_path / "src.vault")
    init_vault(p, "src-pass")
    set_secret(p, "src-pass", "KEY1", "value1")
    set_secret(p, "src-pass", "KEY2", "value2")
    return p


@pytest.fixture
def dst_vault(tmp_path):
    p = str(tmp_path / "dst.vault")
    init_vault(p, "dst-pass")
    return p


def test_copy_all_secrets(src_vault, dst_vault):
    copied = copy_secrets(src_vault, "src-pass", dst_vault, "dst-pass")
    assert set(copied) == {"KEY1", "KEY2"}


def test_copied_secrets_readable(src_vault, dst_vault):
    copy_secrets(src_vault, "src-pass", dst_vault, "dst-pass")
    assert get_secret(dst_vault, "dst-pass", "KEY1") == "value1"
    assert get_secret(dst_vault, "dst-pass", "KEY2") == "value2"


def test_copy_selective_keys(src_vault, dst_vault):
    copied = copy_secrets(src_vault, "src-pass", dst_vault, "dst-pass", keys=["KEY1"])
    assert copied == ["KEY1"]
    with pytest.raises(Exception):
        get_secret(dst_vault, "dst-pass", "KEY2")


def test_copy_missing_key_raises(src_vault, dst_vault):
    with pytest.raises(CopyError, match="MISSING"):
        copy_secrets(src_vault, "src-pass", dst_vault, "dst-pass", keys=["MISSING"])


def test_copy_no_overwrite_by_default(src_vault, dst_vault):
    set_secret(dst_vault, "dst-pass", "KEY1", "original")
    copy_secrets(src_vault, "src-pass", dst_vault, "dst-pass")
    assert get_secret(dst_vault, "dst-pass", "KEY1") == "original"


def test_copy_overwrite_flag(src_vault, dst_vault):
    set_secret(dst_vault, "dst-pass", "KEY1", "original")
    copy_secrets(src_vault, "src-pass", dst_vault, "dst-pass", overwrite=True)
    assert get_secret(dst_vault, "dst-pass", "KEY1") == "value1"


def test_list_copy_candidates(src_vault, dst_vault):
    set_secret(dst_vault, "dst-pass", "KEY1", "x")
    result = list_copy_candidates(src_vault, dst_vault)
    assert result["KEY1"] == "exists"
    assert result["KEY2"] == "new"
