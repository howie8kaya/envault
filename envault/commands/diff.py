"""Diff two environments or a vault env against a local .env file."""

from dataclasses import dataclass
from typing import Optional

from envault.vault import load_vault, VaultError
from envault.crypto import decrypt
from envault.env_io import parse_env, read_env_file, EnvParseError


@dataclass
class DiffEntry:
    key: str
    status: str  # 'added', 'removed', 'changed', 'unchanged'
    vault_value: Optional[str] = None
    file_value: Optional[str] = None

    def __str__(self) -> str:
        if self.status == "added":
            return f"+ {self.key}  (only in file)"
        if self.status == "removed":
            return f"- {self.key}  (only in vault)"
        if self.status == "changed":
            return f"~ {self.key}  (vault != file)"
        return f"  {self.key}  (same)"


def diff_vault_vs_file(
    vault_path: str,
    env_file_path: str,
    passphrase: str,
    env_name: str = "default",
    show_unchanged: bool = False,
) -> list[DiffEntry]:
    """Compare secrets in a vault environment against a local .env file."""
    vault = load_vault(vault_path)

    envs = vault.get("envs", {})
    if env_name not in envs:
        raise VaultError(f"Environment '{env_name}' not found in vault.")

    vault_secrets: dict[str, str] = {}
    for key, ciphertext in envs[env_name].items():
        try:
            vault_secrets[key] = decrypt(ciphertext, passphrase)
        except Exception as exc:
            raise VaultError(f"Failed to decrypt key '{key}': {exc}") from exc

    try:
        raw = read_env_file(env_file_path)
        file_secrets = parse_env(raw)
    except (EnvParseError, OSError) as exc:
        raise VaultError(f"Could not read env file: {exc}") from exc

    all_keys = sorted(set(vault_secrets) | set(file_secrets))
    entries: list[DiffEntry] = []

    for key in all_keys:
        in_vault = key in vault_secrets
        in_file = key in file_secrets

        if in_vault and in_file:
            if vault_secrets[key] == file_secrets[key]:
                status = "unchanged"
            else:
                status = "changed"
        elif in_vault:
            status = "removed"
        else:
            status = "added"

        if status == "unchanged" and not show_unchanged:
            continue

        entries.append(
            DiffEntry(
                key=key,
                status=status,
                vault_value=vault_secrets.get(key),
                file_value=file_secrets.get(key),
            )
        )

    return entries


def format_diff(entries: list[DiffEntry]) -> str:
    """Return a human-readable diff summary."""
    if not entries:
        return "No differences found."
    return "\n".join(str(e) for e in entries)
