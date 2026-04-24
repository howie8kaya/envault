"""Tests for envault.commands.env_chain."""
from __future__ import annotations

import pytest
from pathlib import Path

from envault.vault import init_vault, set_secret
from envault.commands.env_chain import (
    resolve_chain,
    list_chain_candidates,
    ChainError,
    ChainResult,
)


@pytest.fixture()
def vault_a(tmp_path: Path):
    p = tmp_path / "a.vault"
    init_vault(p, "passA")
    set_secret(p, "passA", "SHARED_KEY", "from_a")
    set_secret(p, "passA", "ONLY_A", "alpha")
    return p


@pytest.fixture()
def vault_b(tmp_path: Path):
    p = tmp_path / "b.vault"
    init_vault(p, "passB")
    set_secret(p, "passB", "SHARED_KEY", "from_b")
    set_secret(p, "passB", "ONLY_B", "beta")
    return p


def test_resolve_chain_returns_chain_result(vault_a, vault_b):
    result = resolve_chain([vault_a, vault_b], ["passA", "passB"])
    assert isinstance(result, ChainResult)


def test_later_vault_wins_on_conflict(vault_a, vault_b):
    result = resolve_chain([vault_a, vault_b], ["passA", "passB"])
    assert result.merged["SHARED_KEY"] == "from_b"


def test_earlier_vault_wins_when_reversed(vault_a, vault_b):
    result = resolve_chain([vault_b, vault_a], ["passB", "passA"])
    assert result.merged["SHARED_KEY"] == "from_a"


def test_unique_keys_from_all_vaults_present(vault_a, vault_b):
    result = resolve_chain([vault_a, vault_b], ["passA", "passB"])
    assert "ONLY_A" in result.merged
    assert "ONLY_B" in result.merged


def test_sources_track_winning_vault(vault_a, vault_b):
    result = resolve_chain([vault_a, vault_b], ["passA", "passB"])
    assert result.sources["SHARED_KEY"] == str(vault_b)
    assert result.sources["ONLY_A"] == str(vault_a)


def test_chain_field_contains_all_paths(vault_a, vault_b):
    result = resolve_chain([vault_a, vault_b], ["passA", "passB"])
    assert str(vault_a) in result.chain
    assert str(vault_b) in result.chain


def test_selective_keys_filter(vault_a, vault_b):
    result = resolve_chain([vault_a, vault_b], ["passA", "passB"], keys=["ONLY_A"])
    assert "ONLY_A" in result.merged
    assert "ONLY_B" not in result.merged


def test_mismatched_lengths_raises(vault_a):
    with pytest.raises(ChainError, match="same length"):
        resolve_chain([vault_a], ["passA", "extra"])


def test_empty_vault_list_raises():
    with pytest.raises(ChainError, match="at least one"):
        resolve_chain([], [])


def test_wrong_passphrase_raises(vault_a, vault_b):
    with pytest.raises(ChainError, match="failed to load"):
        resolve_chain([vault_a, vault_b], ["wrong", "passB"])


def test_list_chain_candidates_union(vault_a, vault_b):
    keys = list_chain_candidates([vault_a, vault_b], ["passA", "passB"])
    assert "SHARED_KEY" in keys
    assert "ONLY_A" in keys
    assert "ONLY_B" in keys
    assert keys.count("SHARED_KEY") == 1  # no duplicates


def test_chain_result_str_contains_keys(vault_a, vault_b):
    result = resolve_chain([vault_a, vault_b], ["passA", "passB"])
    text = str(result)
    assert "SHARED_KEY" in text
    assert "ONLY_A" in text
