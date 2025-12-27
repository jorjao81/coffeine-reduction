"""Tests for graph module."""

from __future__ import annotations

from unittest.mock import patch

from src import graph


def test_render_graph_with_data() -> None:
    """Test graph rendering with data."""
    daily_totals = [
        ("2025-12-26", 158),
        ("2025-12-27", 126),
    ]

    with patch("src.graph.plt") as mock_plt:
        graph.render_graph(daily_totals)

        mock_plt.clear_figure.assert_called_once()
        mock_plt.bar.assert_called_once()
        mock_plt.title.assert_called_with("Daily Caffeine Intake")
        mock_plt.xlabel.assert_called_with("Date")
        mock_plt.ylabel.assert_called_with("Caffeine (mg)")
        mock_plt.show.assert_called_once()


def test_render_graph_empty() -> None:
    """Test graph rendering with no data."""
    with patch("src.graph.plt") as mock_plt:
        graph.render_graph([])

        # Should not call any plotext functions
        mock_plt.bar.assert_not_called()
        mock_plt.show.assert_not_called()


def test_render_graph_date_formatting() -> None:
    """Test date formatting in graph."""
    daily_totals = [
        ("2025-12-27", 100),
    ]

    with patch("src.graph.plt") as mock_plt:
        graph.render_graph(daily_totals)

        # Verify dates are formatted as MM-DD
        call_args = mock_plt.bar.call_args
        dates = call_args[0][0]
        assert dates == ["12-27"]


def test_render_graph_multiple_dates() -> None:
    """Test graph with multiple dates formats correctly."""
    daily_totals = [
        ("2025-12-25", 100),
        ("2025-12-26", 150),
        ("2025-12-27", 200),
    ]

    with patch("src.graph.plt") as mock_plt:
        graph.render_graph(daily_totals)

        call_args = mock_plt.bar.call_args
        dates = call_args[0][0]
        values = call_args[0][1]

        assert dates == ["12-25", "12-26", "12-27"]
        assert values == [100, 150, 200]
