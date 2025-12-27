"""Graph rendering for caffeine intake visualization."""

from __future__ import annotations

import plotext as plt


def render_graph(daily_totals: list[tuple[str, int]]) -> None:
    """
    Render a bar chart of daily caffeine totals.

    Args:
        daily_totals: List of (date_str, total_mg) tuples where date_str is ISO format.
    """
    if not daily_totals:
        return

    # Extract dates and values
    dates = [d[0] for d in daily_totals]
    values = [d[1] for d in daily_totals]

    # Format dates for readability (MM-DD)
    formatted_dates = [d[5:] for d in dates]  # "2025-12-27" -> "12-27"

    # Clear any previous plot
    plt.clear_figure()

    # Create bar chart
    plt.bar(formatted_dates, values)
    plt.title("Daily Caffeine Intake")
    plt.xlabel("Date")
    plt.ylabel("Caffeine (mg)")

    # Render to terminal
    plt.show()
