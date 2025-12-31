"""Status display logic for caffeine and sugar tracking."""

from __future__ import annotations

from datetime import datetime

import plotille

from src import data

# Number of days to show in status history
STATUS_HISTORY_DAYS = 10
# Minimum data points required for graph rendering
MIN_GRAPH_DATA_POINTS = 2


def get_status_data() -> tuple[list[tuple[str, str, int, int]], int, int]:
    """
    Get today's status data.

    Returns:
        Tuple of (entries, caffeine_total, sugar_total) where entries is list of
        (timestamp, drink, caffeine_mg, sugar_g)
    """
    entries = data.get_today_entries()
    caffeine_total = sum(mg for _, _, mg, _ in entries)
    sugar_total = sum(sg for _, _, _, sg in entries)
    return entries, caffeine_total, sugar_total


def format_time(iso_timestamp: str) -> str:
    """
    Format ISO timestamp to human-readable time.

    Args:
        iso_timestamp: ISO format timestamp (e.g., "2025-12-27T08:15:00")

    Returns:
        Time string in HH:MM format, or original string if no T separator

    Example:
        "2025-12-27T08:15:00" -> "08:15"
    """
    if "T" in iso_timestamp:
        time_part = iso_timestamp.split("T")[1]
        return time_part[:5]  # HH:MM
    return iso_timestamp


def get_yesterday_comparison() -> tuple[int, int] | None:
    """
    Get comparison between today and yesterday's total.

    Returns:
        Tuple of (caffeine_diff, sugar_diff) or None if no yesterday data
    """
    yesterday_entries = data.get_yesterday_entries()
    if not yesterday_entries:
        return None

    today_caffeine, today_sugar = data.get_today_total()
    yesterday_caffeine = sum(mg for _, _, mg, _ in yesterday_entries)
    yesterday_sugar = sum(sg for _, _, _, sg in yesterday_entries)

    return today_caffeine - yesterday_caffeine, today_sugar - yesterday_sugar


def get_same_time_comparison() -> tuple[int, int] | None:
    """
    Get comparison between today and yesterday at the same time.

    Returns:
        Tuple of (caffeine_diff, sugar_diff) or None if no yesterday data
    """
    yesterday_entries = data.get_yesterday_entries()
    if not yesterday_entries:
        return None

    now = datetime.now()
    today_caffeine, today_sugar = data.get_today_total()

    # Calculate from cached entries instead of extra file read
    cutoff_time = f"{now.hour:02d}:{now.minute:02d}"
    yesterday_caffeine_by_time = sum(
        mg
        for timestamp, _, mg, _ in yesterday_entries
        if "T" in timestamp and timestamp.split("T")[1][:5] <= cutoff_time
    )
    yesterday_sugar_by_time = sum(
        sg
        for timestamp, _, _, sg in yesterday_entries
        if "T" in timestamp and timestamp.split("T")[1][:5] <= cutoff_time
    )

    return today_caffeine - yesterday_caffeine_by_time, today_sugar - yesterday_sugar_by_time


def format_comparison(diff: int, unit: str = "mg") -> str:
    """
    Format comparison difference with sign.

    Args:
        diff: The difference value (today - yesterday)
        unit: Unit to append (default: "mg")

    Returns:
        Formatted string with sign (e.g., "+45mg", "-30mg", "0mg")
    """
    if diff > 0:
        return f"+{diff}{unit}"
    elif diff < 0:
        return f"{diff}{unit}"
    else:
        return f"0{unit}"


def get_history_data() -> list[tuple[str, int, int]]:
    """
    Get the last 10 days of caffeine and sugar totals.

    Returns:
        List of (date_str, caffeine_mg, sugar_g) tuples sorted by date ascending.
    """
    return data.get_daily_totals(STATUS_HISTORY_DAYS)


def render_braille_graph(daily_totals: list[tuple[str, int, int]], width: int = 50, height: int = 8) -> str:
    """
    Render a braille line graph of caffeine intake.

    Args:
        daily_totals: List of (date_str, caffeine_mg, sugar_g) tuples.
        width: Width of the graph in characters.
        height: Height of the graph in characters.

    Returns:
        String containing the braille graph.
    """
    # Need at least MIN_GRAPH_DATA_POINTS for a meaningful line graph
    if len(daily_totals) < MIN_GRAPH_DATA_POINTS:
        return ""

    caffeine_values = [d[1] for d in daily_totals]
    dates = [d[0][5:] for d in daily_totals]  # MM-DD format
    x_values = list(range(len(caffeine_values)))

    # Create the figure
    fig = plotille.Figure()
    fig.width = width
    fig.height = height
    fig.set_x_limits(min_=0, max_=len(caffeine_values) - 1)

    # Set y limits with some padding
    max_val = max(caffeine_values)
    min_val = min(caffeine_values)
    padding = (max_val - min_val) * 0.1 if max_val != min_val else 10
    fig.set_y_limits(min_=max(0, min_val - padding), max_=max_val + padding)

    # Configure x-axis labels - show first and last date
    fig.x_label = f"{dates[0]} → {dates[-1]}"
    fig.y_label = "mg"

    # Plot caffeine line
    fig.plot(x_values, caffeine_values, lc="cyan", label="Caffeine (mg)")

    return str(fig.show(legend=False))  # pyright: ignore[reportUnknownArgumentType]
