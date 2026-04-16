import pytest
from pathlib import Path
from envault.vault import init_vault, set_secret
from envault.commands.notes import (
    set_note, get_note, delete_note, list_notes, NoteError
)

PASS = "hunter2"


@pytest.fixture
def vault_path(tmp_path):
    p = tmp_path / "vault.json"
    init_vault(str(p), PASS)
    set_secret(str(p), PASS, "DB_URL", "postgres://localhost/db")
    set_secret(str(p), PASS, "API_KEY", "abc123")
    return str(p)


def test_set_note_returns_note_info(vault_path):
    info = set_note(vault_path, PASS, "DB_URL", "Production database")
    assert info.key == "DB_URL"
    assert info.note == "Production database"


def test_get_note_returns_set_note(vault_path):
    set_note(vault_path, PASS, "DB_URL", "Main DB")
    info = get_note(vault_path, PASS, "DB_URL")
    assert info is not None
    assert info.note == "Main DB"


def test_get_note_returns_none_when_not_set(vault_path):
    result = get_note(vault_path, PASS, "API_KEY")
    assert result is None


def test_set_note_missing_key_raises(vault_path):
    with pytest.raises(NoteError, match="Key not found"):
        set_note(vault_path, PASS, "GHOST", "nope")


def test_set_note_empty_note_raises(vault_path):
    with pytest.raises(NoteError, match="empty"):
        set_note(vault_path, PASS, "DB_URL", "   ")


def test_delete_note_returns_true(vault_path):
    set_note(vault_path, PASS, "DB_URL", "temp")
    assert delete_note(vault_path, PASS, "DB_URL") is True


def test_delete_note_returns_false_when_none(vault_path):
    assert delete_note(vault_path, PASS, "API_KEY") is False


def test_note_gone_after_delete(vault_path):
    set_note(vault_path, PASS, "DB_URL", "to remove")
    delete_note(vault_path, PASS, "DB_URL")
    assert get_note(vault_path, PASS, "DB_URL") is None


def test_list_notes_returns_all(vault_path):
    set_note(vault_path, PASS, "DB_URL", "note1")
    set_note(vault_path, PASS, "API_KEY", "note2")
    notes = list_notes(vault_path, PASS)
    keys = {n.key for n in notes}
    assert keys == {"DB_URL", "API_KEY"}


def test_list_notes_empty_when_none(vault_path):
    assert list_notes(vault_path, PASS) == []


def test_note_str(vault_path):
    info = set_note(vault_path, PASS, "DB_URL", "hello")
    assert str(info) == "DB_URL: hello"
