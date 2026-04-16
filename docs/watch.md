# Watch

The `watch` command monitors a `.env` file for changes and automatically syncs updated keys into the vault.

## How It Works

`watch_env_file` polls the target file at a configurable interval. When the file hash changes, it computes which keys differ from the previous state and writes only those keys into the vault.

## Usage

```python
from pathlib import Path
from envault.commands.watch import watch_env_file

watch_env_file(
    env_path=Path(".env"),
    vault_path=Path(".envault"),
    passphrase="my-passphrase",
    interval=2.0,          # seconds between polls
    on_change=print,       # optional callback
)
```

Press `Ctrl+C` to stop watching.

## API

### `watch_env_file(env_path, vault_path, passphrase, interval, on_change, max_iterations)`

| Parameter | Type | Description |
|---|---|---|
| `env_path` | `Path` | `.env` file to monitor |
| `vault_path` | `Path` | Vault file to sync into |
| `passphrase` | `str` | Vault passphrase |
| `interval` | `float` | Poll interval in seconds (default `1.0`) |
| `on_change` | `callable` | Optional callback receiving a `WatchEvent` |
| `max_iterations` | `int` | Stop after N polls (useful for testing) |

### `WatchEvent`

```python
@dataclass
class WatchEvent:
    path: Path
    changed_keys: list[str]
    timestamp: float
```

## Errors

- `WatchError` — raised if `env_path` or `vault_path` does not exist at startup.

## Notes

- Only keys whose **values changed** are written to the vault; unchanged keys are left untouched.
- Deleted keys are **not** removed from the vault automatically.
