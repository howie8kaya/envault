import pytest
from envault.vault import init_vault, set_secret
from envault.commands.group import add_to_group, GroupError
from envault.commands.group_export import export_group, group_summary

PASS = "testpass"


@pytest.fixture
def vault_path(tmp_path):
    p = tmp_path / "test.vault"
    init_vault(p, PASS)
    set_secret(p, PASS, "DB_HOST", "localhost")
    set_secret(p, PASS, "DB_PORT", "5432")
    set_secret(p, PASS, "API_KEY", "abc123")
    return p


def test_export_group_contains_keys(vault_path):
    add_to_group(vault_path, PASS, "db", "DB_HOST")
    add_to_group(vault_path, PASS, "db", "DB_PORT")
    result = export_group(vault_path, PASS, "db")
    assert "DB_HOST" in result
    assert "DB_PORT" in result


def test_export_group_values_correct(vault_path):
    add_to_group(vault_path, PASS, "db", "DB_HOST")
    result = export_group(vault_path, PASS, "db")
    assert "localhost" in result


def test_export_group_excludes_other_keys(vault_path):
    add_to_group(vault_path, PASS, "db", "DB_HOST")
    result = export_group(vault_path, PASS, "db")
    assert "API_KEY" not in result


def test_export_nonexistent_group_raises(vault_path):
    with pytest.raises(GroupError, match="does not exist"):
        export_group(vault_path, PASS, "ghost")


def test_group_summary_empty_when_no_groups(vault_path):
    assert group_summary(vault_path, PASS) == []


def test_group_summary_returns_count(vault_path):
    add_to_group(vault_path, PASS, "db", "DB_HOST")
    add_to_group(vault_path, PASS, "db", "DB_PORT")
    summaries = group_summary(vault_path, PASS)
    assert len(summaries) == 1
    assert summaries[0]["group"] == "db"
    assert summaries[0]["count"] == 2


def test_group_summary_multiple_groups(vault_path):
    add_to_group(vault_path, PASS, "db", "DB_HOST")
    add_to_group(vault_path, PASS, "api", "API_KEY")
    summaries = group_summary(vault_path, PASS)
    names = [s["group"] for s in summaries]
    assert "db" in names
    assert "api" in names


def test_group_summary_missing_key_tracked(vault_path):
    add_to_group(vault_path, PASS, "db", "DB_HOST")
    # manually corrupt group meta to include a ghost key
    from envault.vault import load_vault, save_vault
    vault = load_vault(vault_path, PASS)
    vault["__meta__"]["groups"]["db"].append("GHOST_KEY")
    save_vault(vault_path, vault, PASS)
    summaries = group_summary(vault_path, PASS)
    db = next(s for s in summaries if s["group"] == "db")
    assert "GHOST_KEY" in db["missing"]
