import pytest
from pathlib import Path

from envault.commands.env_defaults_io import (
    save_defaults_manifest,
    load_defaults_manifest,
    delete_defaults_manifest,
    DefaultsIOError,
)


@pytest.fixture
def vault_path(tmp_path):
    return tmp_path / "vault.env"


def test_save_and_load_roundtrip(vault_path):
    defaults = {"FOO": "bar", "PORT": "8080"}
    save_defaults_manifest(vault_path, defaults)
    loaded = load_defaults_manifest(vault_path)
    assert loaded == defaults


def test_save_creates_json_file(vault_path):
    save_defaults_manifest(vault_path, {"A": "1"})
    manifest = vault_path.with_suffix(".defaults.json")
    assert manifest.exists()
    assert manifest.suffix == ".json"


def test_load_missing_manifest_raises(vault_path):
    with pytest.raises(DefaultsIOError, match="No defaults manifest"):
        load_defaults_manifest(vault_path)


def test_load_invalid_json_raises(vault_path):
    manifest = vault_path.with_suffix(".defaults.json")
    manifest.write_text("not json", encoding="utf-8")
    with pytest.raises(DefaultsIOError, match="Invalid JSON"):
        load_defaults_manifest(vault_path)


def test_load_non_object_raises(vault_path):
    manifest = vault_path.with_suffix(".defaults.json")
    manifest.write_text("[1, 2, 3]", encoding="utf-8")
    with pytest.raises(DefaultsIOError, match="must be a JSON object"):
        load_defaults_manifest(vault_path)


def test_save_non_dict_raises(vault_path):
    with pytest.raises(DefaultsIOError):
        save_defaults_manifest(vault_path, ["not", "a", "dict"])  # type: ignore


def test_delete_returns_true_when_exists(vault_path):
    save_defaults_manifest(vault_path, {"X": "1"})
    assert delete_defaults_manifest(vault_path) is True


def test_delete_returns_false_when_missing(vault_path):
    assert delete_defaults_manifest(vault_path) is False


def test_delete_removes_file(vault_path):
    save_defaults_manifest(vault_path, {"X": "1"})
    delete_defaults_manifest(vault_path)
    manifest = vault_path.with_suffix(".defaults.json")
    assert not manifest.exists()
