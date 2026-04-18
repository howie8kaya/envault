"""Tests for envault.commands.env_stats."""
import pytest
from pathlib import Path
from envault.vault import init_vault, set_secret
from envault.commands.env_stats import vault_stats, VaultStats, StatsError


@pytest.fixture
def vault_path(tmp_path: Path) -> str:
    p = str(tmp_path / "test.vault")
    init_vault(p, "pass")
    return p


def test_stats_empty_vault_returns_zeros(vault_path):
    stats = vault_stats(vault_path, "pass")
    assert stats.total_keys == 0
    assert stats.empty_values == 0
    assert stats.avg_value_length == 0.0


def test_stats_counts_keys(vault_path):
    set_secret(vault_path, "pass", "KEY1", "value1")
    set_secret(vault_path, "pass", "KEY2", "value2")
    stats = vault_stats(vault_path, "pass")
    assert stats.total_keys == 2


def test_stats_detects_empty_value(vault_path):
    set_secret(vault_path, "pass", "EMPTY", "")
    stats = vault_stats(vault_path, "pass")
    assert stats.empty_values == 1


def test_stats_detects_short_value(vault_path):
    set_secret(vault_path, "pass", "SHORT", "abc")
    stats = vault_stats(vault_path, "pass")
    assert stats.short_values == 1


def test_stats_detects_long_value(vault_path):
    set_secret(vault_path, "pass", "LONG", "a" * 40)
    stats = vault_stats(vault_path, "pass")
    assert stats.long_values == 1


def test_stats_avg_value_length(vault_path):
    set_secret(vault_path, "pass", "A", "ab")    # len 2
    set_secret(vault_path, "pass", "B", "abcd")  # len 4
    stats = vault_stats(vault_path, "pass")
    assert stats.avg_value_length == pytest.approx(3.0)


def test_stats_keys_list(vault_path):
    set_secret(vault_path, "pass", "FOO", "bar")
    stats = vault_stats(vault_path, "pass")
    assert "FOO" in stats.keys


def test_stats_wrong_passphrase_raises(vault_path):
    set_secret(vault_path, "pass", "K", "v")
    with pytest.raises(StatsError):
        vault_stats(vault_path, "wrongpass")


def test_stats_str_output(vault_path):
    set_secret(vault_path, "pass", "X", "hello")
    stats = vault_stats(vault_path, "pass")
    out = str(stats)
    assert "Total keys" in out
    assert "Avg value len" in out
