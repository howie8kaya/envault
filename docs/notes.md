# Notes

Attach human-readable notes to individual secrets in your vault.

## Overview

Notes are plaintext annotations stored in vault metadata. They are useful for
documenting the purpose of a secret, its rotation schedule, or any other context
your team needs.

## API

### `set_note(vault_path, passphrase, key, note) -> NoteInfo`

Attach or overwrite a note on the given key.

- Raises `NoteError` if the key does not exist.
- Raises `NoteError` if the note is blank.

### `get_note(vault_path, passphrase, key) -> NoteInfo | None`

Retrieve the note for a key. Returns `None` if no note is set.

### `delete_note(vault_path, passphrase, key) -> bool`

Remove the note from a key. Returns `True` if a note was deleted, `False` if
no note existed.

### `list_notes(vault_path, passphrase) -> list[NoteInfo]`

Return all notes stored in the vault.

## NoteInfo

| Field | Type | Description |
|-------|------|-------------|
| `key` | str  | Secret key  |
| `note`| str  | Note text   |

`str(note_info)` returns `"KEY: note text"`.

## Example

```python
from envault.commands.notes import set_note, get_note, list_notes

set_note("vault.json", "passphrase", "DB_URL", "Rotates every 90 days")

info = get_note("vault.json", "passphrase", "DB_URL")
print(info)  # DB_URL: Rotates every 90 days

for n in list_notes("vault.json", "passphrase"):
    print(n)
```
