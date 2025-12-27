"""Tests for drinks database module."""

from __future__ import annotations

from src.drinks_db import DRINKS_DB, get_caffeine


def test_get_caffeine_known_drink() -> None:
    """Test lookup of known drink."""
    assert get_caffeine("espresso") == 63
    assert get_caffeine("coffee") == 95
    assert get_caffeine("tea") == 47


def test_get_caffeine_case_insensitive() -> None:
    """Test case-insensitive lookup."""
    assert get_caffeine("ESPRESSO") == 63
    assert get_caffeine("Espresso") == 63
    assert get_caffeine("COFFEE") == 95
    assert get_caffeine("Coffee") == 95


def test_get_caffeine_unknown_drink() -> None:
    """Test lookup of unknown drink returns None."""
    assert get_caffeine("unknown_drink_xyz") is None
    assert get_caffeine("made_up_beverage") is None


def test_get_caffeine_strips_whitespace() -> None:
    """Test that whitespace is stripped from drink names."""
    assert get_caffeine("  espresso  ") == 63
    assert get_caffeine(" coffee") == 95
    assert get_caffeine("tea ") == 47


def test_drinks_db_has_common_drinks() -> None:
    """Test that common drinks are in the database."""
    common_drinks = ["espresso", "coffee", "latte", "tea", "cola", "energy drink", "red bull"]
    for drink in common_drinks:
        assert drink in DRINKS_DB, f"Expected {drink} to be in DRINKS_DB"


def test_all_caffeine_values_positive() -> None:
    """Test that all caffeine values are positive integers."""
    for drink, mg in DRINKS_DB.items():
        assert isinstance(mg, int), f"Caffeine for {drink} should be int"
        assert mg >= 0, f"Caffeine for {drink} should be non-negative"
