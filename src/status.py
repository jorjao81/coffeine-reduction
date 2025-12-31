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


def calculate_hourly_blood_concentration(
    days: int = STATUS_HISTORY_DAYS,
) -> list[tuple[datetime, float]]:
    """
    Calculate blood caffeine concentration at each hour over the specified days.

    Uses pharmacokinetic decay model with configurable half-life.
    For each hour, calculates remaining caffeine from all prior consumption.

    Args:
        days: Number of days to calculate concentration for.

    Returns:
        List of (datetime, concentration_mg) tuples sorted chronologically.
    """
    from datetime import timedelta

    all_entries = data.get_all_entries()
    if not all_entries:
        return []

    # Parse all entries into (datetime, caffeine_mg) for easier calculation
    parsed_entries: list[tuple[datetime, int]] = []
    for timestamp, _, mg, _ in all_entries:
        try:
            dt = datetime.fromisoformat(timestamp)
            parsed_entries.append((dt, mg))
        except ValueError:
            continue

    if not parsed_entries:
        return []

    # Build hourly timestamps for the last N days
    now = datetime.now()
    # For today, only go up to current hour
    current_hour = now.replace(minute=0, second=0, microsecond=0)
    start_date = now.date() - timedelta(days=days - 1)
    start_dt = datetime(start_date.year, start_date.month, start_date.day, 0, 0, 0)

    # Generate hourly timestamps
    hourly_timestamps: list[datetime] = []
    current_dt = start_dt
    while current_dt <= current_hour:
        hourly_timestamps.append(current_dt)
        current_dt += timedelta(hours=1)

    # Calculate concentration at each hour
    results: list[tuple[datetime, float]] = []
    for target_dt in hourly_timestamps:
        concentration = 0.0

        for entry_dt, mg in parsed_entries:
            # Only consider drinks consumed before the target time
            if entry_dt <= target_dt:
                hours_elapsed = (target_dt - entry_dt).total_seconds() / 3600
                # Apply decay formula: C(t) = C0 * 0.5^(t/half_life)
                remaining = mg * (0.5 ** (hours_elapsed / CAFFEINE_HALF_LIFE_HOURS))
                concentration += remaining

        results.append((target_dt, concentration))

    # Trim leading zeros
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
    hourly_concentration: list[tuple[datetime, float]] | None = None,
    width: int = 100,
    height: int = 8,
) -> str:
    """
    Render a braille line graph of caffeine intake and hourly blood concentration.

    Args:
        daily_totals: List of (date_str, caffeine_mg, sugar_g) tuples.
        hourly_concentration: Optional list of (datetime, concentration_mg) tuples.
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

    # Calculate the time span in hours for the x-axis
    # Use first date at 00:00 as origin, last date at 23:59 as end
    first_date = datetime.fromisoformat(f"{daily_totals[0][0]}T00:00:00")
    last_date = datetime.fromisoformat(f"{daily_totals[-1][0]}T23:59:59")
    total_hours = (last_date - first_date).total_seconds() / 3600

    # Map daily totals to x positions (center of each day = noon)
    daily_x_values: list[float] = []
    for date_str, _, _ in daily_totals:
        day_noon = datetime.fromisoformat(f"{date_str}T12:00:00")
        hours_from_start = (day_noon - first_date).total_seconds() / 3600
        daily_x_values.append(hours_from_start)

    # Map hourly concentration to x positions
    concentration_x_values: list[float] = []
    concentration_y_values: list[float] = []
    if hourly_concentration:
        for dt, conc in hourly_concentration:
            hours_from_start = (dt - first_date).total_seconds() / 3600
            if 0 <= hours_from_start <= total_hours:
                concentration_x_values.append(hours_from_start)
                concentration_y_values.append(conc)

    # Create the figure
    fig = plotille.Figure()
    fig.width = width
    fig.height = height
    fig.set_x_limits(min_=0, max_=total_hours)

    # Set y limits considering both series
    all_values = caffeine_values + concentration_y_values
    max_val = max(all_values) if all_values else 0
    min_val = min(all_values) if all_values else 0
    padding = (max_val - min_val) * 0.1 if max_val != min_val else 10
    fig.set_y_limits(min_=max(0, min_val - padding), max_=max_val + padding)

    # Configure x-axis labels - show first and last date
    fig.x_label = f"{dates[0]} → {dates[-1]}"
    fig.y_label = "mg"

    # Plot caffeine intake line (daily totals)
    fig.plot(daily_x_values, caffeine_values, lc="cyan", label="Intake")

    # Plot blood concentration line if available (hourly)
    if concentration_x_values:
        fig.plot(concentration_x_values, concentration_y_values, lc="yellow", label="Blood")

    output = str(fig.show(legend=True))  # pyright: ignore[reportUnknownArgumentType]

    # Round y-axis labels for cleaner display
    import re

    def round_match(m: re.Match[str]) -> str:
        return str(round(float(m.group(0))))

    # Match floating point numbers at the start of lines (y-axis labels)
    output = re.sub(r"^[\d.]+(?=\s*\|)", round_match, output, flags=re.MULTILINE)
    return output


def _calculate_concentration_at_time(target_dt: datetime, parsed_entries: list[tuple[datetime, int]]) -> float:
    """Calculate blood caffeine concentration at a specific time."""
    concentration = 0.0
    for entry_dt, mg in parsed_entries:
        if entry_dt <= target_dt:
            hours_elapsed = (target_dt - entry_dt).total_seconds() / 3600
            remaining = mg * (0.5 ** (hours_elapsed / CAFFEINE_HALF_LIFE_HOURS))
            concentration += remaining
    return concentration


def _parse_entries_to_datetime(
    entries: list[tuple[str, str, int, int]],
) -> list[tuple[datetime, int]]:
    """Parse entry timestamps to datetime objects."""
    parsed: list[tuple[datetime, int]] = []
    for timestamp, _, mg, _ in entries:
        try:
            parsed.append((datetime.fromisoformat(timestamp), mg))
        except ValueError:
            continue
    return parsed


def _get_24h_time_points(today_entries: list[tuple[str, str, int, int]], now: datetime) -> list[float]:
    """Get time points for 24h graph including drink times for sharp spikes."""
    time_points: set[float] = set()

    # Add hourly points
    for hour in range(now.hour + 1):
        time_points.add(float(hour))

    # Add drink times (as fractional hours) - before and after for sharp spikes
    for ts, _, _, _ in today_entries:
        if _is_valid_timestamp(ts):
            dt = datetime.fromisoformat(ts)
            if dt.date() == now.date():
                fractional_hour = dt.hour + dt.minute / 60.0
                time_points.add(max(0, fractional_hour - 0.017))  # ~1 min before
                time_points.add(fractional_hour)

    return sorted(time_points)


def _get_drink_times(today_entries: list[tuple[str, str, int, int]], now: datetime) -> list[tuple[float, int, str]]:
    """Extract drink times as (fractional_hour, mg, name) tuples."""
    drink_times: list[tuple[float, int, str]] = []
    for ts, name, mg, _ in today_entries:
        if _is_valid_timestamp(ts):
            dt = datetime.fromisoformat(ts)
            if dt.date() == now.date():
                fractional_hour = dt.hour + dt.minute / 60.0
                drink_times.append((fractional_hour, mg, name))
    return drink_times


def render_24h_graph(
    today_entries: list[tuple[str, str, int, int]],
    width: int = 100,
    height: int = 6,
) -> str:
    """Render a 24-hour blood concentration graph with drink markers."""
    import re
    from datetime import timedelta

    all_entries = data.get_all_entries()
    if not all_entries:
        return ""

    parsed_entries = _parse_entries_to_datetime(all_entries)
    if not parsed_entries:
        return ""

    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # Build graph data with sharp spikes at drink times
    sorted_times = _get_24h_time_points(today_entries, now)
    graph_data = [
        (t, _calculate_concentration_at_time(today_start + timedelta(hours=t), parsed_entries))
        for t in sorted_times
        if today_start + timedelta(hours=t) <= now
    ]

    if len(graph_data) < MIN_GRAPH_DATA_POINTS:
        return ""

    x_values = [t for t, _ in graph_data]
    y_values = [c for _, c in graph_data]
    conc_lookup = dict(graph_data)
    drink_times = _get_drink_times(today_entries, now)

    # Create figure
    fig = plotille.Figure()
    fig.width = width
    fig.height = height
    fig.set_x_limits(min_=0, max_=now.hour + 1)

    max_val, min_val = (max(y_values), min(y_values)) if y_values else (0, 0)
    padding = (max_val - min_val) * 0.1 if max_val != min_val else 10
    fig.set_y_limits(min_=max(0, min_val - padding), max_=max_val + padding)
    fig.x_label = "00:00 → now"
    fig.y_label = "mg"
    fig.plot(x_values, y_values, lc="yellow", label="Blood")

    # Add drink markers
    marker_x = [t for t, _, _ in drink_times if t in conc_lookup]
    marker_y = [conc_lookup[t] for t, _, _ in drink_times if t in conc_lookup]
    if marker_x:
        fig.scatter(marker_x, marker_y, lc="cyan", marker="x")

    output = str(fig.show(legend=False))  # pyright: ignore[reportUnknownArgumentType]
    output = re.sub(r"^[\d.]+(?=\s*\|)", lambda m: str(round(float(m.group(0)))), output, flags=re.MULTILINE)

    # Add drink annotations
    if drink_times:
        annotations = [f"☕ {int(t):02d}:{int((t - int(t)) * 60):02d} {name} ({mg}mg)" for t, mg, name in drink_times]
        output += f"\n  {'  '.join(annotations)}"

    return output


def _is_valid_timestamp(ts: str) -> bool:
    """Check if a timestamp string is valid ISO format."""
    try:
        datetime.fromisoformat(ts)
        return True
    except ValueError:
        return False
