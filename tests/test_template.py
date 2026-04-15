"""Tests for envault.commands.template."""

from __future__ import annotations

import pytest
from pathlib import Path

from envault.vault import init_vault, set_secret
from envault.commands.template import (
    render_template,
    render_template_file,
    RenderResult,
    TemplateError,
)

PASS = "hunter2"


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    vp = tmp_path / "test.vault"
    init_vault(vp, PASS)
    set_secret(vp, "DB_HOST", "localhost", PASS)
    set_secret(vp, "DB_PORT", "5432", PASS)
    set_secret(vp, "API_KEY", "secret-abc", PASS)
    return vp


def test_render_simple_substitution(vault_path: Path) -> None:
    tmpl = "host={{DB_HOST}} port={{DB_PORT}}"
    result = render_template(tmpl, vault_path, PASS)
    assert result.output == "host=localhost port=5432"
    assert set(result.substituted) == {"DB_HOST", "DB_PORT"}
    assert result.missing == []


def test_render_result_has_missing(vault_path: Path) -> None:
    tmpl = "key={{MISSING_KEY}}"
    result = render_template(tmpl, vault_path, PASS)
    assert "MISSING_KEY" in result.missing
    assert "{{MISSING_KEY}}" in result.output  # placeholder preserved
    assert result.has_missing is True


def test_render_strict_raises_on_missing(vault_path: Path) -> None:
    tmpl = "key={{DOES_NOT_EXIST}}"
    with pytest.raises(TemplateError, match="DOES_NOT_EXIST"):
        render_template(tmpl, vault_path, PASS, strict=True)


def test_render_no_placeholders(vault_path: Path) -> None:
    tmpl = "nothing to replace here"
    result = render_template(tmpl, vault_path, PASS)
    assert result.output == tmpl
    assert result.substituted == []
    assert result.missing == []


def test_render_whitespace_in_placeholder(vault_path: Path) -> None:
    tmpl = "{{ DB_HOST }}"
    result = render_template(tmpl, vault_path, PASS)
    assert result.output == "localhost"


def test_render_template_file(vault_path: Path, tmp_path: Path) -> None:
    tmpl_file = tmp_path / "config.tmpl"
    tmpl_file.write_text("API_KEY={{API_KEY}}\n")
    result = render_template_file(tmpl_file, vault_path, PASS)
    assert result.output == "secret-abc\n"
    assert "API_KEY" in result.substituted


def test_render_template_file_writes_output(vault_path: Path, tmp_path: Path) -> None:
    tmpl_file = tmp_path / "config.tmpl"
    out_file = tmp_path / "config.env"
    tmpl_file.write_text("DB_HOST={{DB_HOST}}\n")
    render_template_file(tmpl_file, vault_path, PASS, output_path=out_file)
    assert out_file.read_text() == "DB_HOST=localhost\n"


def test_render_template_file_missing_file(vault_path: Path, tmp_path: Path) -> None:
    with pytest.raises(TemplateError, match="not found"):
        render_template_file(tmp_path / "ghost.tmpl", vault_path, PASS)


def test_render_wrong_passphrase_raises(vault_path: Path) -> None:
    tmpl = "{{DB_HOST}}"
    with pytest.raises(Exception):
        render_template(tmpl, vault_path, "wrongpass", strict=True)
