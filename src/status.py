"""Status display logic for caffeine and sugar tracking."""

from __future__ import annotations

from datetime import datetime

import plotille

from src import data

# Number of days to show in status history
STATUS_HISTORY_DAYS = 10
# Minimum data points required for graph rendering
MIN_GRAPH_DATA_POINTS = 2
# Caffeine half-life in hours (average adult)
CAFFEINE_HALF_LIFE_HOURS = 5
# Threshold for considering concentration non-zero (floating point tolerance)
CONCENTRATION_THRESHOLD = 0.1


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


def calculate_daily_blood_concentration(
    days: int = STATUS_HISTORY_DAYS,
) -> list[tuple[str, float]]:
    """
    Calculate blood caffeine concentration at end of each day.

    Uses pharmacokinetic decay model with configurable half-life.
    For each target day, calculates remaining caffeine at 23:59 from all
    prior consumption.

    Args:
        days: Number of days to calculate concentration for.

    Returns:
        List of (date_str, concentration_mg) tuples sorted by date ascending.
    """
    from datetime import timedelta

    all_entries = data.get_all_entries()
    if not all_entries:
        return []

    # Build target dates (last N days)
    today = datetime.now().date()
    target_dates = [(today - timedelta(days=i)).isoformat() for i in range(days - 1, -1, -1)]

    # Parse all entries into (datetime, caffeine_mg) for easier calculation
    parsed_entries: list[tuple[datetime, int]] = []
    for timestamp, _, mg, _ in all_entries:
        try:
            dt = datetime.fromisoformat(timestamp)
            parsed_entries.append((dt, mg))
        except ValueError:
            continue

    results: list[tuple[str, float]] = []
    for date_str in target_dates:
        # Calculate concentration at end of this day (23:59:59)
        target_dt = datetime.fromisoformat(f"{date_str}T23:59:59")
        concentration = 0.0

        for entry_dt, mg in parsed_entries:
            # Only consider drinks consumed before the target time
            if entry_dt <= target_dt:
                hours_elapsed = (target_dt - entry_dt).total_seconds() / 3600
                # Apply decay formula: C(t) = C0 * 0.5^(t/half_life)
                remaining = mg * (0.5 ** (hours_elapsed / CAFFEINE_HALF_LIFE_HOURS))
                concentration += remaining

        results.append((date_str, concentration))

    # Trim leading zeros like get_daily_totals does
    first_nonzero_idx = None
    for i, (_, conc) in enumerate(results):
        if conc > CONCENTRATION_THRESHOLD:
            first_nonzero_idx = i
            break

    if first_nonzero_idx is not None:
        return results[first_nonzero_idx:]

    return []


def render_braille_graph(
    daily_totals: list[tuple[str, int, int]],
    blood_concentration: list[tuple[str, float]] | None = None,
    width: int = 50,
    height: int = 8,
) -> str:
    """
    Render a braille line graph of caffeine intake and blood concentration.

    Args:
        daily_totals: List of (date_str, caffeine_mg, sugar_g) tuples.
        blood_concentration: Optional list of (date_str, concentration_mg) tuples.
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

    # Build blood concentration values aligned to the same dates
    concentration_values: list[float] = []
    if blood_concentration:
        conc_dict = {d[0]: d[1] for d in blood_concentration}
        concentration_values = [conc_dict.get(d[0], 0.0) for d in daily_totals]

    # Create the figure
    fig = plotille.Figure()
    fig.width = width
    fig.height = height
    fig.set_x_limits(min_=0, max_=len(caffeine_values) - 1)

    # Set y limits considering both series
    all_values = caffeine_values + concentration_values
    max_val = max(all_values) if all_values else 0
    min_val = min(all_values) if all_values else 0
    padding = (max_val - min_val) * 0.1 if max_val != min_val else 10
    fig.set_y_limits(min_=max(0, min_val - padding), max_=max_val + padding)

    # Configure x-axis labels - show first and last date
    fig.x_label = f"{dates[0]} → {dates[-1]}"
    fig.y_label = "mg"

    # Plot caffeine intake line
    fig.plot(x_values, caffeine_values, lc="cyan", label="Intake")

    # Plot blood concentration line if available
    if concentration_values:
        fig.plot(x_values, concentration_values, lc="yellow", label="Blood")

    return str(fig.show(legend=True))  # pyright: ignore[reportUnknownArgumentType]
