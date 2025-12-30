"""Graph rendering for caffeine and sugar intake visualization."""

from __future__ import annotations

import plotext as plt


def render_graph(daily_totals: list[tuple[str, int, int]]) -> None:
    """
    Render bar charts of daily caffeine and sugar totals.

    Args:
        daily_totals: List of (date_str, caffeine_mg, sugar_g) tuples where date_str is ISO format.
    """
    if not daily_totals:
        return

    # Extract dates and values
    dates = [d[0] for d in daily_totals]
    caffeine_values = [d[1] for d in daily_totals]
    sugar_values = [d[2] for d in daily_totals]

    # Format dates for readability (MM-DD)
    formatted_dates = [d[5:] for d in dates]  # "2025-12-27" -> "12-27"

    # Clear any previous plot
    plt.clear_figure()

    # Create side-by-side bar chart
    plt.multiple_bar(formatted_dates, [caffeine_values, sugar_values], labels=["Caffeine (mg)", "Sugar (g)"])
    plt.title("Daily Caffeine & Sugar Intake")
    plt.xlabel("Date")

    # Render to terminal
    plt.show()
