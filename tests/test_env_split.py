"""Tests for envault.commands.env_split."""

import pytest
from pathlib import Path

from envault.vault import init_vault, set_secret, get_secret
from envault.commands.env_split import (
    SplitError,
    SplitResult,
    split_by_prefix,
    split_by_map,
)

PASS = "testpass"


@pytest.fixture
def vault_path(tmp_path):
    p = tmp_path / "source.vault"
    init_vault(p, PASS)
    set_secret(p, PASS, "DB_HOST", "localhost")
    set_secret(p, PASS, "DB_PORT", "5432")
    set_secret(p, PASS, "APP_SECRET", "abc123")
    set_secret(p, PASS, "APP_DEBUG", "false")
    set_secret(p, PASS, "CACHE_URL", "redis://localhost")
    return p


def test_split_by_prefix_returns_result(vault_path, tmp_path):
    prefix_map = {
        "DB_": tmp_path / "db.vault",
        "APP_": tmp_path / "app.vault",
    }
    result = split_by_prefix(vault_path, PASS, prefix_map)
    assert isinstance(result, SplitResult)
    assert "DB_" in result.shards
    assert "APP_" in result.shards


def test_split_by_prefix_correct_counts(vault_path, tmp_path):
    prefix_map = {
        "DB_": tmp_path / "db.vault",
        "APP_": tmp_path / "app.vault",
    }
    result = split_by_prefix(vault_path, PASS, prefix_map)
    assert result.counts["DB_"] == 2
    assert result.counts["APP_"] == 2


def test_split_by_prefix_values_readable(vault_path, tmp_path):
    db_path = tmp_path / "db.vault"
    result = split_by_prefix(vault_path, PASS, {"DB_": db_path})
    assert get_secret(db_path, PASS, "DB_HOST") == "localhost"
    assert get_secret(db_path, PASS, "DB_PORT") == "5432"


def test_split_by_prefix_strip_prefix(vault_path, tmp_path):
    db_path = tmp_path / "db.vault"
    split_by_prefix(vault_path, PASS, {"DB_": db_path}, strip_prefix=True)
    assert get_secret(db_path, PASS, "HOST") == "localhost"
    assert get_secret(db_path, PASS, "PORT") == "5432"


def test_split_by_prefix_skips_unmatched_prefix(vault_path, tmp_path):
    result = split_by_prefix(
        vault_path, PASS, {"NOMATCH_": tmp_path / "nomatch.vault"}
    )
    assert "NOMATCH_" not in result.shards


def test_split_by_map_returns_result(vault_path, tmp_path):
    key_map = {
        "db": ["DB_HOST", "DB_PORT"],
        "app": ["APP_SECRET"],
    }
    result = split_by_map(vault_path, PASS, key_map, tmp_path)
    assert isinstance(result, SplitResult)
    assert "db" in result.shards
    assert "app" in result.shards


def test_split_by_map_values_readable(vault_path, tmp_path):
    key_map = {"cache": ["CACHE_URL"]}
    result = split_by_map(vault_path, PASS, key_map, tmp_path)
    shard_path = result.shards["cache"]
    assert get_secret(shard_path, PASS, "CACHE_URL") == "redis://localhost"


def test_split_by_map_missing_key_raises(vault_path, tmp_path):
    key_map = {"bad": ["NONEXISTENT_KEY"]}
    with pytest.raises(SplitError, match="NONEXISTENT_KEY"):
        split_by_map(vault_path, PASS, key_map, tmp_path)


def test_split_result_str(vault_path, tmp_path):
    prefix_map = {"DB_": tmp_path / "db.vault"}
    result = split_by_prefix(vault_path, PASS, prefix_map)
    text = str(result)
    assert "db.vault" in text
    assert "2 key(s)" in text


def test_split_by_map_creates_dest_dir(vault_path, tmp_path):
    dest_dir = tmp_path / "shards" / "nested"
    key_map = {"db": ["DB_HOST"]}
    split_by_map(vault_path, PASS, key_map, dest_dir)
    assert dest_dir.exists()
