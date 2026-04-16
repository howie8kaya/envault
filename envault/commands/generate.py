"""Generate random secret values for vault keys."""
import secrets
import string
from dataclasses import dataclass
from pathlib import Path

from envault.vault import load_vault, save_vault, VaultError


class GenerateError(Exception):
    pass


@dataclass
class GenerateResult:
    key: str
    value: str
    length: int
    charset: str

    def __str__(self):
        return f"{self.key} = {'*' * self.length}  ({self.length} chars, {self.charset})"


_CHARSETS = {
    "alphanumeric": string.ascii_letters + string.digits,
    "alpha": string.ascii_letters,
    "numeric": string.digits,
    "hex": string.hexdigits[:16],
    "full": string.ascii_letters + string.digits + string.punctuation,
}


def generate_secret(
    vault_path: Path,
    passphrase: str,
    key: str,
    length: int = 32,
    charset: str = "alphanumeric",
    overwrite: bool = False,
) -> GenerateResult:
    """Generate a random secret and store it in the vault."""
    if length < 1:
        raise GenerateError("Length must be at least 1")
    if charset not in _CHARSETS:
        raise GenerateError(f"Unknown charset '{charset}'. Choose from: {', '.join(_CHARSETS)}")

    vault = load_vault(vault_path, passphrase)

    if key in vault and not overwrite:
        raise GenerateError(f"Key '{key}' already exists. Use overwrite=True to replace it.")

    alphabet = _CHARSETS[charset]
    value = "".join(secrets.choice(alphabet) for _ in range(length))

    vault[key] = value
    save_vault(vault_path, passphrase, vault)

    return GenerateResult(key=key, value=value, length=length, charset=charset)


def list_charsets() -> list[str]:
    """Return available charset names."""
    return list(_CHARSETS.keys())
