"""Tests for envault.commands.env_summary."""

import pytest

from envault.vault import init_vault, set_secret
from envault.commands.env_summary import (
    SummaryError,
    SummaryEntry,
    VaultSummary,
    summarize_vault,
    _preview,
)


@pytest.fixture
def vault_path(tmp_path):
    p = str(tmp_path / "test.vault")
    init_vault(p, "pass")
    return p


def test_summarize_returns_vault_summary(vault_path):
    set_secret(vault_path, "pass", "KEY_A", "hello")
    result = summarize_vault(vault_path, "pass")
    assert isinstance(result, VaultSummary)


def test_summarize_total_keys(vault_path):
    set_secret(vault_path, "pass", "KEY_A", "hello")
    set_secret(vault_path, "pass", "KEY_B", "world")
    result = summarize_vault(vault_path, "pass")
    assert result.total_keys == 2


def test_summarize_empty_vault_returns_zeros(vault_path):
    result = summarize_vault(vault_path, "pass")
    assert result.total_keys == 0
    assert result.empty_keys == 0
    assert result.avg_length == 0.0


def test_summarize_detects_empty_value(vault_path):
    set_secret(vault_path, "pass", "EMPTY_KEY", "")
    result = summarize_vault(vault_path, "pass")
    assert result.empty_keys == 1


def test_summarize_avg_length(vault_path):
    set_secret(vault_path, "pass", "A", "ab")    # len 2
    set_secret(vault_path, "pass", "B", "abcd")  # len 4
    result = summarize_vault(vault_path, "pass")
    assert result.avg_length == pytest.approx(3.0)


def test_summarize_selective_keys(vault_path):
    set_secret(vault_path, "pass", "KEY_A", "hello")
    set_secret(vault_path, "pass", "KEY_B", "world")
    result = summarize_vault(vault_path, "pass", keys=["KEY_A"])
    assert result.total_keys == 1
    assert result.entries[0].key == "KEY_A"


def test_summarize_missing_key_raises(vault_path):
    set_secret(vault_path, "pass", "KEY_A", "hello")
    with pytest.raises(SummaryError, match="MISSING"):
        summarize_vault(vault_path, "pass", keys=["MISSING"])


def test_summary_entry_str(vault_path):
    set_secret(vault_path, "pass", "MY_KEY", "secret123")
    result = summarize_vault(vault_path, "pass")
    entry_str = str(result.entries[0])
    assert "MY_KEY" in entry_str
    assert "9 chars" in entry_str


def test_vault_summary_str(vault_path):
    set_secret(vault_path, "pass", "KEY_A", "value")
    result = summarize_vault(vault_path, "pass")
    text = str(result)
    assert "Keys" in text
    assert "KEY_A" in text


def test_preview_reveals_first_chars():
    assert _preview("abcdefgh", reveal=4) == "abcd****"


def test_preview_empty_string():
    assert _preview("") == ""


def test_preview_short_value():
    assert _preview("ab", reveal=4) == "ab"


def test_entries_sorted_alphabetically(vault_path):
    set_secret(vault_path, "pass", "ZEBRA", "z")
    set_secret(vault_path, "pass", "ALPHA", "a")
    result = summarize_vault(vault_path, "pass")
    keys = [e.key for e in result.entries]
    assert keys == sorted(keys)
