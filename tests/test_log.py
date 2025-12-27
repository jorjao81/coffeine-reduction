"""Tests for drink logging business logic."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

import src.data as data_module
from src.log import log_drink


def test_log_drink_known_drink(tmp_path: Path) -> None:
    """Test logging a known drink returns correct values."""
    test_dir = tmp_path / "data"
    test_file = test_dir / "drinks.tsv"

    with patch.object(data_module, "DATA_DIR", test_dir), patch.object(data_module, "DRINKS_FILE", test_file):
        drink_name, caffeine, total = log_drink("espresso")

        assert drink_name == "espresso"
        assert caffeine == 63
        assert total == 63  # First drink of the day


def test_log_drink_case_insensitive(tmp_path: Path) -> None:
    """Test that drink names are case-insensitive."""
    test_dir = tmp_path / "data"
    test_file = test_dir / "drinks.tsv"

    with patch.object(data_module, "DATA_DIR", test_dir), patch.object(data_module, "DRINKS_FILE", test_file):
        drink_name, caffeine, _ = log_drink("ESPRESSO")

        assert drink_name == "espresso"  # Normalized to lowercase
        assert caffeine == 63


def test_log_drink_updates_running_total(tmp_path: Path) -> None:
    """Test that running total accumulates."""
    test_dir = tmp_path / "data"
    test_file = test_dir / "drinks.tsv"

    with patch.object(data_module, "DATA_DIR", test_dir), patch.object(data_module, "DRINKS_FILE", test_file):
        _, _, total1 = log_drink("espresso")
        _, _, total2 = log_drink("coffee")

        assert total1 == 63
        assert total2 == 158  # 63 + 95


def test_log_drink_unknown_raises_error(tmp_path: Path) -> None:
    """Test that unknown drinks raise ValueError."""
    test_dir = tmp_path / "data"
    test_file = test_dir / "drinks.tsv"

    with patch.object(data_module, "DATA_DIR", test_dir), patch.object(data_module, "DRINKS_FILE", test_file):
        with pytest.raises(ValueError, match="Unknown drink"):
            log_drink("made_up_beverage_xyz")


def test_log_drink_rejects_tabs(tmp_path: Path) -> None:
    """Test that drink names with tabs are rejected."""
    test_dir = tmp_path / "data"
    test_file = test_dir / "drinks.tsv"

    with patch.object(data_module, "DATA_DIR", test_dir), patch.object(data_module, "DRINKS_FILE", test_file):
        with pytest.raises(ValueError, match="tabs or newlines"):
            log_drink("espresso\tdangerous")


def test_log_drink_rejects_newlines(tmp_path: Path) -> None:
    """Test that drink names with newlines are rejected."""
    test_dir = tmp_path / "data"
    test_file = test_dir / "drinks.tsv"

    with patch.object(data_module, "DATA_DIR", test_dir), patch.object(data_module, "DRINKS_FILE", test_file):
        with pytest.raises(ValueError, match="tabs or newlines"):
            log_drink("espresso\nevil")


def test_log_drink_rejects_empty(tmp_path: Path) -> None:
    """Test that empty drink names are rejected."""
    test_dir = tmp_path / "data"
    test_file = test_dir / "drinks.tsv"

    with patch.object(data_module, "DATA_DIR", test_dir), patch.object(data_module, "DRINKS_FILE", test_file):
        with pytest.raises(ValueError, match="cannot be empty"):
            log_drink("   ")


def test_log_drink_strips_whitespace(tmp_path: Path) -> None:
    """Test that whitespace is stripped from drink names."""
    test_dir = tmp_path / "data"
    test_file = test_dir / "drinks.tsv"

    with patch.object(data_module, "DATA_DIR", test_dir), patch.object(data_module, "DRINKS_FILE", test_file):
        drink_name, caffeine, _ = log_drink("  espresso  ")

        assert drink_name == "espresso"
        assert caffeine == 63


def test_log_drink_creates_file(tmp_path: Path) -> None:
    """Test that logging creates the data file."""
    test_dir = tmp_path / "data"
    test_file = test_dir / "drinks.tsv"

    with patch.object(data_module, "DATA_DIR", test_dir), patch.object(data_module, "DRINKS_FILE", test_file):
        log_drink("espresso")

        assert test_file.exists()
        content = test_file.read_text()
        assert "espresso" in content
        assert "63" in content


def test_log_drink_with_custom_mg(tmp_path: Path) -> None:
    """Test logging unknown drink with custom caffeine amount."""
    test_dir = tmp_path / "data"
    test_file = test_dir / "drinks.tsv"

    with patch.object(data_module, "DATA_DIR", test_dir), patch.object(data_module, "DRINKS_FILE", test_file):
        drink_name, caffeine, total = log_drink("weird energy drink", mg=200)

        assert drink_name == "weird energy drink"
        assert caffeine == 200
        assert total == 200


def test_log_drink_known_with_mg_override(tmp_path: Path) -> None:
    """Test that --mg overrides database value for known drinks."""
    test_dir = tmp_path / "data"
    test_file = test_dir / "drinks.tsv"

    with patch.object(data_module, "DATA_DIR", test_dir), patch.object(data_module, "DRINKS_FILE", test_file):
        drink_name, caffeine, total = log_drink("espresso", mg=100)

        assert drink_name == "espresso"
        assert caffeine == 100  # Override, not 63 from database
        assert total == 100


def test_log_drink_zero_mg_allowed(tmp_path: Path) -> None:
    """Test that zero caffeine is allowed (for decaf tracking)."""
    test_dir = tmp_path / "data"
    test_file = test_dir / "drinks.tsv"

    with patch.object(data_module, "DATA_DIR", test_dir), patch.object(data_module, "DRINKS_FILE", test_file):
        drink_name, caffeine, total = log_drink("decaf custom", mg=0)

        assert drink_name == "decaf custom"
        assert caffeine == 0
        assert total == 0


def test_log_drink_negative_mg_rejected(tmp_path: Path) -> None:
    """Test that negative caffeine values are rejected."""
    test_dir = tmp_path / "data"
    test_file = test_dir / "drinks.tsv"

    with patch.object(data_module, "DATA_DIR", test_dir), patch.object(data_module, "DRINKS_FILE", test_file):
        with pytest.raises(ValueError, match="cannot be negative"):
            log_drink("weird drink", mg=-50)
