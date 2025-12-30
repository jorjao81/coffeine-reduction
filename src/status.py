"""Status display logic for caffeine and sugar tracking."""

from __future__ import annotations

from datetime import datetime

from src import data


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
