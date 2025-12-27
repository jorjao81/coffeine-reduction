"""Status display logic for caffeine tracking."""

from __future__ import annotations

from datetime import datetime

from src import data


def get_status_data() -> tuple[list[tuple[str, str, int]], int]:
    """
    Get today's status data.

    Returns:
        Tuple of (entries, total) where entries is list of (timestamp, drink, mg)
    """
    entries = data.get_today_entries()
    total = sum(mg for _, _, mg in entries)  # Calculate from entries, avoid extra file read
    return entries, total


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


def get_yesterday_comparison() -> int | None:
    """
    Get comparison between today and yesterday's total.

    Returns:
        Difference (today - yesterday) or None if no yesterday data
    """
    yesterday_entries = data.get_yesterday_entries()
    if not yesterday_entries:
        return None

    today_total = data.get_today_total()
    yesterday_total = sum(mg for _, _, mg in yesterday_entries)  # Calculate from cached entries

    return today_total - yesterday_total


def get_same_time_comparison() -> int | None:
    """
    Get comparison between today and yesterday at the same time.

    Returns:
        Difference (today - yesterday_by_time) or None if no yesterday data
    """
    yesterday_entries = data.get_yesterday_entries()
    if not yesterday_entries:
        return None

    now = datetime.now()
    today_total = data.get_today_total()

    # Calculate from cached entries instead of extra file read
    cutoff_time = f"{now.hour:02d}:{now.minute:02d}"
    yesterday_by_time = sum(
        mg for timestamp, _, mg in yesterday_entries if "T" in timestamp and timestamp.split("T")[1][:5] <= cutoff_time
    )

    return today_total - yesterday_by_time


def format_comparison(diff: int) -> str:
    """
    Format comparison difference with sign.

    Args:
        diff: The difference value (today - yesterday)

    Returns:
        Formatted string with sign (e.g., "+45mg", "-30mg", "0mg")
    """
    if diff > 0:
        return f"+{diff}mg"
    elif diff < 0:
        return f"{diff}mg"
    else:
        return "0mg"
