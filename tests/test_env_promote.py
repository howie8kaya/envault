import pytest
from pathlib import Path
from envault.vault import init_vault, set_secret, get_secret
from envault.commands.env_promote import promote_secrets, list_promote_candidates, PromoteError


@pytest.fixture
def src_vault(tmp_path):
    p = tmp_path / "src.vault"
    init_vault(p, "src-pass")
    set_secret(p, "src-pass", "DB_URL", "postgres://src")
    set_secret(p, "src-pass", "API_KEY", "src-api-key")
    set_secret(p, "src-pass", "SHARED", "shared-value")
    return p


@pytest.fixture
def dst_vault(tmp_path):
    p = tmp_path / "dst.vault"
    init_vault(p, "dst-pass")
    set_secret(p, "dst-pass", "SHARED", "old-value")
    return p


def test_promote_all_new_keys(src_vault, dst_vault):
    promoted = promote_secrets(src_vault, dst_vault, "src-pass", "dst-pass")
    assert "DB_URL" in promoted
    assert "API_KEY" in promoted


def test_promoted_values_readable(src_vault, dst_vault):
    promote_secrets(src_vault, dst_vault, "src-pass", "dst-pass")
    assert get_secret(dst_vault, "dst-pass", "DB_URL") == "postgres://src"


def test_existing_key_skipped_by_default(src_vault, dst_vault):
    promoted = promote_secrets(src_vault, dst_vault, "src-pass", "dst-pass")
    assert "SHARED" not in promoted
    assert get_secret(dst_vault, "dst-pass", "SHARED") == "old-value"


def test_existing_key_overwritten_when_flag_set(src_vault, dst_vault):
    promoted = promote_secrets(src_vault, dst_vault, "src-pass", "dst-pass", overwrite=True)
    assert "SHARED" in promoted
    assert get_secret(dst_vault, "dst-pass", "SHARED") == "shared-value"


def test_promote_selective_keys(src_vault, dst_vault):
    promoted = promote_secrets(src_vault, dst_vault, "src-pass", "dst-pass", keys=["API_KEY"])
    assert promoted == ["API_KEY"]


def test_promote_missing_key_raises(src_vault, dst_vault):
    with pytest.raises(PromoteError, match="MISSING"):
        promote_secrets(src_vault, dst_vault, "src-pass", "dst-pass", keys=["MISSING"])


def test_list_candidates(src_vault, dst_vault):
    result = list_promote_candidates(src_vault, dst_vault, "src-pass", "dst-pass")
    assert "DB_URL" in result["new"]
    assert "API_KEY" in result["new"]
    assert "SHARED" in result["existing"]


def test_list_candidates_empty_dst(src_vault, tmp_path):
    empty = tmp_path / "empty.vault"
    init_vault(empty, "pass")
    result = list_promote_candidates(src_vault, empty, "src-pass", "pass")
    assert set(result["new"]) == {"DB_URL", "API_KEY", "SHARED"}
    assert result["existing"] == []
