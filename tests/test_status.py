"""Tests for status module."""

from __future__ import annotations

from unittest.mock import patch

from src import status


def test_get_status_data_with_entries() -> None:
    """Test status data with drinks logged."""
    mock_entries = [
        ("2025-12-27T08:15:00", "baly", 60, 27),
        ("2025-12-27T10:30:00", "red bull", 80, 27),
    ]
    with patch("src.status.data.get_today_entries", return_value=mock_entries):
        entries, caffeine_total, sugar_total = status.get_status_data()
        assert len(entries) == 2
        assert caffeine_total == 140
        assert sugar_total == 54


def test_get_status_data_empty() -> None:
    """Test status data with no drinks logged."""
    with patch("src.status.data.get_today_entries", return_value=[]):
        entries, caffeine_total, sugar_total = status.get_status_data()
        assert entries == []
        assert caffeine_total == 0
        assert sugar_total == 0


def test_format_time_with_t_separator() -> None:
    """Test ISO timestamp to time formatting with T separator."""
    assert status.format_time("2025-12-27T08:15:00") == "08:15"
    assert status.format_time("2025-12-27T14:30:45") == "14:30"


def test_format_time_without_t() -> None:
    """Test format_time returns input when no T separator."""
    assert status.format_time("08:15:00") == "08:15:00"
    assert status.format_time("invalid") == "invalid"


def test_get_yesterday_comparison_with_data() -> None:
    """Test yesterday comparison when data exists."""
    mock_entries = [("ts", "drink", 100, 30)]
    with patch("src.status.data.get_yesterday_entries", return_value=mock_entries):
        with patch("src.status.data.get_today_total", return_value=(80, 20)):
            diff = status.get_yesterday_comparison()
            assert diff == (-20, -10)  # Reduced by 20mg caffeine, 10g sugar


def test_get_yesterday_comparison_no_data() -> None:
    """Test yesterday comparison when no yesterday data."""
    with patch("src.status.data.get_yesterday_entries", return_value=[]):
        diff = status.get_yesterday_comparison()
        assert diff is None


def test_get_same_time_comparison_with_data() -> None:
    """Test same-time comparison when data exists."""
    # Entry at 00:01 - always before current time so always included
    mock_entries = [("2025-12-27T00:01:00", "baly", 100, 30)]
    with patch("src.status.data.get_yesterday_entries", return_value=mock_entries):
        with patch("src.status.data.get_today_total", return_value=(80, 20)):
            diff = status.get_same_time_comparison()
            # Today 80mg/20g, yesterday at 00:01 had 100mg/30g (always before current time)
            assert diff == (-20, -10)  # (80-100, 20-30)


def test_get_same_time_comparison_no_data() -> None:
    """Test same-time comparison when no yesterday data."""
    with patch("src.status.data.get_yesterday_entries", return_value=[]):
        diff = status.get_same_time_comparison()
        assert diff is None


def test_format_comparison_positive() -> None:
    """Test comparison formatting for positive difference."""
    assert status.format_comparison(45) == "+45mg"
    assert status.format_comparison(45, "g") == "+45g"


def test_format_comparison_negative() -> None:
    """Test comparison formatting for negative difference."""
    assert status.format_comparison(-30) == "-30mg"
    assert status.format_comparison(-30, "g") == "-30g"


def test_format_comparison_zero() -> None:
    """Test comparison formatting for zero."""
    assert status.format_comparison(0) == "0mg"
    assert status.format_comparison(0, "g") == "0g"
