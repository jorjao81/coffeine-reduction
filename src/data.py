"""Data persistence layer for drink logging."""

from __future__ import annotations

import tomllib
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

DATA_DIR = Path("./data")
DRINKS_FILE = DATA_DIR / "drinks.tsv"
CONFIG_FILE = DATA_DIR / "config.toml"

# TSV column count
TSV_COLUMNS = 3

# Default graph settings
DEFAULT_GRAPH_DAYS = 14


def ensure_data_dir() -> None:
    """Create data directory if it doesn't exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def append_drink(timestamp: str, drink: str, caffeine_mg: int) -> None:
    """Append a drink entry to the TSV log. Creates file with header if needed."""
    ensure_data_dir()

    # Check if file needs header
    needs_header = not DRINKS_FILE.exists() or DRINKS_FILE.stat().st_size == 0

    with DRINKS_FILE.open("a") as f:
        if needs_header:
            f.write("timestamp\tdrink\tcaffeine_mg\n")
        f.write(f"{timestamp}\t{drink}\t{caffeine_mg}\n")


def get_today_entries() -> list[tuple[str, str, int]]:
    """Read all entries from today. Returns list of (timestamp, drink, mg)."""
    if not DRINKS_FILE.exists():
        return []

    today = datetime.now().date().isoformat()
    entries: list[tuple[str, str, int]] = []

    with DRINKS_FILE.open() as f:
        # Skip header line
        header = next(f, None)
        if header is None:
            return []

        for line in f:
            parts = line.strip().split("\t")
            if len(parts) == TSV_COLUMNS and parts[0].startswith(today):
                try:
                    caffeine_mg = int(parts[2])
                    entries.append((parts[0], parts[1], caffeine_mg))
                except ValueError:
                    # Skip corrupted rows with non-integer caffeine values
                    continue

    return entries


def get_today_total() -> int:
    """Calculate today's total caffeine intake."""
    return sum(mg for _, _, mg in get_today_entries())


def get_yesterday_date() -> str:
    """Get yesterday's date in ISO format (YYYY-MM-DD)."""
    yesterday = datetime.now().date() - timedelta(days=1)
    return yesterday.isoformat()


def get_yesterday_entries() -> list[tuple[str, str, int]]:
    """Read all entries from yesterday. Returns list of (timestamp, drink, mg)."""
    if not DRINKS_FILE.exists():
        return []

    yesterday = get_yesterday_date()
    entries: list[tuple[str, str, int]] = []

    with DRINKS_FILE.open() as f:
        header = next(f, None)
        if header is None:
            return []

        for line in f:
            parts = line.strip().split("\t")
            if len(parts) == TSV_COLUMNS and parts[0].startswith(yesterday):
                try:
                    caffeine_mg = int(parts[2])
                    entries.append((parts[0], parts[1], caffeine_mg))
                except ValueError:
                    continue

    return entries


def get_yesterday_total() -> int:
    """Calculate yesterday's total caffeine intake."""
    return sum(mg for _, _, mg in get_yesterday_entries())


def get_yesterday_total_by_time(hour: int, minute: int) -> int:
    """
    Calculate yesterday's caffeine total up to a specific time.

    Args:
        hour: Hour (0-23)
        minute: Minute (0-59)

    Returns:
        Total caffeine consumed yesterday before or at the specified time
    """
    cutoff_time = f"{hour:02d}:{minute:02d}"
    total = 0

    for timestamp, _, mg in get_yesterday_entries():
        if "T" in timestamp:
            time_part = timestamp.split("T")[1][:5]
            if time_part <= cutoff_time:
                total += mg

    return total


# ============================================================================
# Config Loading (Story 3.1)
# ============================================================================


def load_config() -> dict[str, Any]:
    """
    Load config from TOML file.

    Returns:
        Config dictionary, or empty dict if file doesn't exist or is malformed.
    """
    if not CONFIG_FILE.exists():
        return {}

    try:
        with CONFIG_FILE.open("rb") as f:
            return tomllib.load(f)
    except tomllib.TOMLDecodeError:
        # Malformed config file - return empty dict to use defaults
        return {}


def get_graph_days() -> int:
    """
    Get number of days to show in graph from config.

    Returns:
        Number of days from config, or DEFAULT_GRAPH_DAYS (14) if not configured
        or if the configured value is invalid.
    """
    config = load_config()
    display = config.get("display", {})
    days = display.get("graph_days", DEFAULT_GRAPH_DAYS)

    # Validate: must be a positive integer
    if not isinstance(days, int) or days < 1:
        return DEFAULT_GRAPH_DAYS

    return days


# ============================================================================
# Historical Data (Story 3.1)
# ============================================================================


def get_all_entries() -> list[tuple[str, str, int]]:
    """
    Read all entries from drinks.tsv.

    Returns:
        List of (timestamp, drink, caffeine_mg) tuples.
    """
    if not DRINKS_FILE.exists():
        return []

    entries: list[tuple[str, str, int]] = []
    with DRINKS_FILE.open() as f:
        header = next(f, None)
        if header is None:
            return []

        for line in f:
            parts = line.strip().split("\t")
            if len(parts) == TSV_COLUMNS:
                try:
                    caffeine_mg = int(parts[2])
                    entries.append((parts[0], parts[1], caffeine_mg))
                except ValueError:
                    continue
    return entries


def get_daily_totals(days: int) -> list[tuple[str, int]]:
    """
    Get daily caffeine totals for the last N days.

    Args:
        days: Number of days to include in the range.

    Returns:
        List of (date_str, total_mg) sorted by date ascending.
        Only includes days from the first day with data through today.
        Days with no drinks logged show as 0mg.
    """
    # Build date range (oldest to newest)
    today = datetime.now().date()
    date_range = [(today - timedelta(days=i)).isoformat() for i in range(days - 1, -1, -1)]

    # Aggregate by date
    daily_sums: dict[str, int] = defaultdict(int)
    for timestamp, _, mg in get_all_entries():
        date_part = timestamp.split("T")[0] if "T" in timestamp else timestamp[:10]
        daily_sums[date_part] += mg

    # If no data at all, return empty
    if not daily_sums:
        return []

    # Build result with zeros for missing days
    result: list[tuple[str, int]] = []
    for date in date_range:
        result.append((date, daily_sums.get(date, 0)))

    # Find first day with data and trim from there
    first_data_idx = None
    for i, (_, mg) in enumerate(result):
        if mg > 0:
            first_data_idx = i
            break

    if first_data_idx is not None:
        return result[first_data_idx:]

    return []
