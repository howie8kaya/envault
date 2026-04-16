import pytest
from pathlib import Path
from envault.vault import init_vault, set_secret
from envault.commands.tags import add_tag, remove_tag, list_tags, filter_by_tag, TagError

PASS = "test-pass"


@pytest.fixture
def vault_path(tmp_path):
    p = tmp_path / "vault.json"
    init_vault(str(p), PASS)
    set_secret(str(p), PASS, "DB_URL", "postgres://localhost/db")
    set_secret(str(p), PASS, "API_KEY", "abc123")
    set_secret(str(p), PASS, "SECRET_TOKEN", "tok_xyz")
    return str(p)


def test_add_tag_returns_tag_list(vault_path):
    result = add_tag(vault_path, PASS, "DB_URL", "database")
    assert "database" in result


def test_add_tag_idempotent(vault_path):
    add_tag(vault_path, PASS, "DB_URL", "database")
    result = add_tag(vault_path, PASS, "DB_URL", "database")
    assert result.count("database") == 1


def test_add_tag_missing_key_raises(vault_path):
    with pytest.raises(TagError, match="not found"):
        add_tag(vault_path, PASS, "MISSING_KEY", "tag")


def test_remove_tag(vault_path):
    add_tag(vault_path, PASS, "API_KEY", "external")
    result = remove_tag(vault_path, PASS, "API_KEY", "external")
    assert "external" not in result


def test_remove_tag_not_present_raises(vault_path):
    with pytest.raises(TagError, match="not present"):
        remove_tag(vault_path, PASS, "API_KEY", "nonexistent")


def test_list_tags_all_keys(vault_path):
    summaries = list_tags(vault_path, PASS)
    keys = [s.key for s in summaries]
    assert "DB_URL" in keys
    assert "API_KEY" in keys


def test_list_tags_shows_assigned_tags(vault_path):
    add_tag(vault_path, PASS, "SECRET_TOKEN", "auth")
    summaries = list_tags(vault_path, PASS)
    token_summary = next(s for s in summaries if s.key == "SECRET_TOKEN")
    assert "auth" in token_summary.tags


def test_filter_by_tag(vault_path):
    add_tag(vault_path, PASS, "DB_URL", "infra")
    add_tag(vault_path, PASS, "API_KEY", "infra")
    results = filter_by_tag(vault_path, PASS, "infra")
    assert "DB_URL" in results
    assert "API_KEY" in results
    assert "SECRET_TOKEN" not in results


def test_filter_by_tag_no_matches(vault_path):
    results = filter_by_tag(vault_path, PASS, "nonexistent-tag")
    assert results == []


def test_tag_summary_str(vault_path):
    add_tag(vault_path, PASS, "DB_URL", "database")
    summaries = list_tags(vault_path, PASS)
    db = next(s for s in summaries if s.key == "DB_URL")
    assert "database" in str(db)
