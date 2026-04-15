"""Utilities for parsing and serializing .env files."""

from pathlib import Path
from typing import Dict


class EnvParseError(Exception):
    pass


def parse_env(text: str) -> Dict[str, str]:
    """Parse the contents of a .env file into a dict.

    Supports:
    - KEY=VALUE
    - KEY="VALUE" or KEY='VALUE' (quotes stripped)
    - Lines starting with # are comments
    - Blank lines are ignored
    """
    result: Dict[str, str] = {}
    for lineno, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise EnvParseError(
                f"Line {lineno}: missing '=' in {raw_line!r}"
            )
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if not key:
            raise EnvParseError(f"Line {lineno}: empty key in {raw_line!r}")
        # Strip matching surrounding quotes
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
            value = value[1:-1]
        result[key] = value
    return result


def serialize_env(secrets: Dict[str, str]) -> str:
    """Serialize a dict of secrets back to .env file format."""
    lines = []
    for key, value in sorted(secrets.items()):
        # Quote values that contain spaces or special characters
        if any(c in value for c in (" ", "\t", "#", "'", '"')):
            escaped = value.replace('"', '\\"')
            lines.append(f'{key}="{escaped}"')
        else:
            lines.append(f"{key}={value}")
    return "\n".join(lines) + ("\n" if lines else "")


def read_env_file(path: Path) -> Dict[str, str]:
    """Read and parse a .env file from disk."""
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise EnvParseError(f"File not found: {path}")
    return parse_env(text)


def write_env_file(path: Path, secrets: Dict[str, str]) -> None:
    """Serialize secrets and write them to a .env file on disk."""
    path.write_text(serialize_env(secrets), encoding="utf-8")
