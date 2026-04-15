"""Tests for team sharing (export/import bundle) functionality."""

from __future__ import annotations

import pytest
from pathlib import Path

from envault.vault import init_vault, set_secret, get_secret
from envault.commands.share import export_shared_bundle, import_shared_bundle, ShareError


PASSPHRASE = "owner-secret-pass"
RECIPIENT_PASS = "recipient-secret-pass"


@pytest.fixture
def vault_path(tmp_path: Path) -> Path:
    path = tmp_path / "test.vault"
    init_vault(path, PASSPHRASE)
    set_secret(path, PASSPHRASE, "DB_URL", "postgres://localhost/db")
    set_secret(path, PASSPHRASE, "API_KEY", "supersecret")
    return path


def test_export_bundle_returns_string(vault_path):
    bundle = export_shared_bundle(vault_path, PASSPHRASE, RECIPIENT_PASS)
    assert isinstance(bundle, str)
    assert len(bundle) > 0


def test_export_bundle_selective_keys(vault_path):
    bundle = export_shared_bundle(vault_path, PASSPHRASE, RECIPIENT_PASS, keys=["API_KEY"])
    assert isinstance(bundle, str)


def test_export_bundle_missing_key_raises(vault_path):
    with pytest.raises(ShareError, match="Keys not found"):
        export_shared_bundle(vault_path, PASSPHRASE, RECIPIENT_PASS, keys=["MISSING_KEY"])


def test_import_bundle_into_new_vault(vault_path, tmp_path):
    bundle = export_shared_bundle(vault_path, PASSPHRASE, RECIPIENT_PASS)

    new_vault = tmp_path / "new.vault"
    new_pass = "new-vault-pass"
    init_vault(new_vault, new_pass)

    count = import_shared_bundle(new_vault, new_pass, bundle, RECIPIENT_PASS)
    assert count == 2

    assert get_secret(new_vault, new_pass, "DB_URL") == "postgres://localhost/db"
    assert get_secret(new_vault, new_pass, "API_KEY") == "supersecret"


def test_import_bundle_no_overwrite_by_default(vault_path, tmp_path):
    bundle = export_shared_bundle(vault_path, PASSPHRASE, RECIPIENT_PASS)

    new_vault = tmp_path / "new.vault"
    new_pass = "new-vault-pass"
    init_vault(new_vault, new_pass)
    set_secret(new_vault, new_pass, "API_KEY", "already-here")

    count = import_shared_bundle(new_vault, new_pass, bundle, RECIPIENT_PASS, overwrite=False)
    assert count == 1  # only DB_URL imported
    assert get_secret(new_vault, new_pass, "API_KEY") == "already-here"


def test_import_bundle_with_overwrite(vault_path, tmp_path):
    bundle = export_shared_bundle(vault_path, PASSPHRASE, RECIPIENT_PASS)

    new_vault = tmp_path / "new.vault"
    new_pass = "new-vault-pass"
    init_vault(new_vault, new_pass)
    set_secret(new_vault, new_pass, "API_KEY", "old-value")

    import_shared_bundle(new_vault, new_pass, bundle, RECIPIENT_PASS, overwrite=True)
    assert get_secret(new_vault, new_pass, "API_KEY") == "supersecret"


def test_import_invalid_bundle_raises(vault_path):
    with pytest.raises(ShareError, match="Invalid bundle format"):
        import_shared_bundle(vault_path, PASSPHRASE, "not-a-valid-bundle!!", RECIPIENT_PASS)


def test_export_empty_vault_raises(tmp_path):
    empty_vault = tmp_path / "empty.vault"
    init_vault(empty_vault, PASSPHRASE)
    with pytest.raises(ShareError, match="No secrets"):
        export_shared_bundle(empty_vault, PASSPHRASE, RECIPIENT_PASS)
