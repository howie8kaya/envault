"""Template generation from vault secrets.

Allows users to render template files using secrets stored in the vault,
substituting {{KEY}} placeholders with decrypted values.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from envault.vault import load_vault, get_secret, VaultError


class TemplateError(Exception):
    """Raised when template rendering fails."""


@dataclass
class RenderResult:
    output: str
    substituted: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)

    @property
    def has_missing(self) -> bool:
        return len(self.missing) > 0


_PLACEHOLDER_RE = re.compile(r"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}")


def render_template(
    template_text: str,
    vault_path: Path,
    passphrase: str,
    *,
    strict: bool = False,
) -> RenderResult:
    """Render *template_text* by replacing {{KEY}} with vault secrets.

    Args:
        template_text: Raw template string containing {{KEY}} placeholders.
        vault_path: Path to the .vault file.
        passphrase: Passphrase used to decrypt secrets.
        strict: If True, raise TemplateError when a key is not found in vault.

    Returns:
        RenderResult with the rendered output and metadata.
    """
    vault = load_vault(vault_path)
    substituted: list[str] = []
    missing: list[str] = []

    def _replace(match: re.Match) -> str:
        key = match.group(1)
        try:
            value = get_secret(vault, key, passphrase)
            substituted.append(key)
            return value
        except VaultError:
            if strict:
                raise TemplateError(
                    f"Template key '{key}' not found in vault '{vault_path}'"
                )
            missing.append(key)
            return match.group(0)  # leave placeholder unchanged

    output = _PLACEHOLDER_RE.sub(_replace, template_text)
    return RenderResult(output=output, substituted=substituted, missing=missing)


def render_template_file(
    template_path: Path,
    vault_path: Path,
    passphrase: str,
    output_path: Optional[Path] = None,
    *,
    strict: bool = False,
) -> RenderResult:
    """Read *template_path*, render it, and optionally write to *output_path*."""
    if not template_path.exists():
        raise TemplateError(f"Template file not found: {template_path}")

    template_text = template_path.read_text(encoding="utf-8")
    result = render_template(template_text, vault_path, passphrase, strict=strict)

    if output_path is not None:
        output_path.write_text(result.output, encoding="utf-8")

    return result
