"""Tests for drinks database module."""

from __future__ import annotations

from src.drinks_db import DRINKS_DB, get_caffeine, get_drink_info, get_sugar


def test_get_caffeine_known_drink() -> None:
    """Test lookup of known drink."""
    assert get_caffeine("baly") == 60
    assert get_caffeine("red bull") == 80
    assert get_caffeine("pepsi max") == 69


def test_get_caffeine_case_insensitive() -> None:
    """Test case-insensitive lookup."""
    assert get_caffeine("BALY") == 60
    assert get_caffeine("Baly") == 60
    assert get_caffeine("RED BULL") == 80
    assert get_caffeine("Red Bull") == 80


def test_get_caffeine_unknown_drink() -> None:
    """Test lookup of unknown drink returns None."""
    assert get_caffeine("unknown_drink_xyz") is None
    assert get_caffeine("made_up_beverage") is None


def test_get_caffeine_strips_whitespace() -> None:
    """Test that whitespace is stripped from drink names."""
    assert get_caffeine("  baly  ") == 60
    assert get_caffeine(" red bull") == 80
    assert get_caffeine("pepsi max ") == 69


def test_drinks_db_has_common_drinks() -> None:
    """Test that common drinks are in the database."""
    common_drinks = ["baly", "red bull", "pepsi max", "fruki"]
    for drink in common_drinks:
        assert drink in DRINKS_DB, f"Expected {drink} to be in DRINKS_DB"


def test_all_caffeine_values_positive() -> None:
    """Test that all caffeine values are positive integers."""
    for drink, info in DRINKS_DB.items():
        assert isinstance(info.caffeine_mg, int), f"Caffeine for {drink} should be int"
        assert info.caffeine_mg >= 0, f"Caffeine for {drink} should be non-negative"


def test_get_sugar_known_drink() -> None:
    """Test sugar lookup for known drinks."""
    assert get_sugar("baly") == 27
    assert get_sugar("red bull") == 27
    assert get_sugar("pepsi max") == 0  # Zero sugar variant


def test_get_sugar_unknown_drink() -> None:
    """Test sugar lookup for unknown drink returns None."""
    assert get_sugar("unknown_drink") is None


def test_get_drink_info() -> None:
    """Test get_drink_info returns complete info."""
    info = get_drink_info("baly")
    assert info is not None
    assert info.caffeine_mg == 60
    assert info.sugar_g == 27


def test_all_sugar_values_non_negative() -> None:
    """Test that all sugar values are non-negative integers."""
    for drink, info in DRINKS_DB.items():
        assert isinstance(info.sugar_g, int), f"Sugar for {drink} should be int"
        assert info.sugar_g >= 0, f"Sugar for {drink} should be non-negative"
