import pytest
from pathlib import Path
from envault.vault import init_vault, set_secret, get_secret, load_vault
from envault.commands.merge import merge_vaults, format_merge_results, MergeError

PASSPHRASE = "test-pass"


@pytest.fixture
def src_vault(tmp_path):
    p = tmp_path / "src.vault"
    v = init_vault(str(p), PASSPHRASE)
    set_secret(v, "API_KEY", "abc123", PASSPHRASE)
    set_secret(v, "DB_URL", "postgres://localhost/db", PASSPHRASE)
    from envault.vault import save_vault
    save_vault(str(p), v, PASSPHRASE)
    return str(p)


@pytest.fixture
def dst_vault(tmp_path):
    p = tmp_path / "dst.vault"
    v = init_vault(str(p), PASSPHRASE)
    set_secret(v, "EXISTING", "value", PASSPHRASE)
    from envault.vault import save_vault
    save_vault(str(p), v, PASSPHRASE)
    return str(p)


def test_merge_all_keys(src_vault, dst_vault):
    results = merge_vaults(src_vault, PASSPHRASE, dst_vault, PASSPHRASE)
    assert len(results) == 2
    actions = {r.key: r.action for r in results}
    assert actions["API_KEY"] == "added"
    assert actions["DB_URL"] == "added"


def test_merged_secrets_readable(src_vault, dst_vault):
    merge_vaults(src_vault, PASSPHRASE, dst_vault, PASSPHRASE)
    v = load_vault(dst_vault, PASSPHRASE)
    assert get_secret(v, "API_KEY", PASSPHRASE) == "abc123"
    assert get_secret(v, "DB_URL", PASSPHRASE) == "postgres://localhost/db"


def test_existing_key_skipped_by_default(src_vault, dst_vault):
    from envault.vault import save_vault
    v = load_vault(dst_vault, PASSPHRASE)
    set_secret(v, "API_KEY", "original", PASSPHRASE)
    save_vault(dst_vault, v, PASSPHRASE)

    results = merge_vaults(src_vault, PASSPHRASE, dst_vault, PASSPHRASE)
    actions = {r.key: r.action for r in results}
    assert actions["API_KEY"] == "skipped"
    v2 = load_vault(dst_vault, PASSPHRASE)
    assert get_secret(v2, "API_KEY", PASSPHRASE) == "original"


def test_overwrite_flag_updates_existing(src_vault, dst_vault):
    from envault.vault import save_vault
    v = load_vault(dst_vault, PASSPHRASE)
    set_secret(v, "API_KEY", "original", PASSPHRASE)
    save_vault(dst_vault, v, PASSPHRASE)

    results = merge_vaults(src_vault, PASSPHRASE, dst_vault, PASSPHRASE, overwrite=True)
    actions = {r.key: r.action for r in results}
    assert actions["API_KEY"] == "updated"
    v2 = load_vault(dst_vault, PASSPHRASE)
    assert get_secret(v2, "API_KEY", PASSPHRASE) == "abc123"


def test_merge_selective_keys(src_vault, dst_vault):
    results = merge_vaults(src_vault, PASSPHRASE, dst_vault, PASSPHRASE, keys=["API_KEY"])
    assert len(results) == 1
    assert results[0].key == "API_KEY"


def test_merge_missing_key_raises(src_vault, dst_vault):
    with pytest.raises(MergeError, match="MISSING_KEY"):
        merge_vaults(src_vault, PASSPHRASE, dst_vault, PASSPHRASE, keys=["MISSING_KEY"])


def test_format_merge_results_includes_summary(src_vault, dst_vault):
    results = merge_vaults(src_vault, PASSPHRASE, dst_vault, PASSPHRASE)
    output = format_merge_results(results)
    assert "added" in output
    assert "Summary" in output


def test_format_empty_results():
    assert format_merge_results([]) == "Nothing to merge."
