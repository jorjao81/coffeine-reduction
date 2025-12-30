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

# TSV column count (timestamp, drink, caffeine_mg, sugar_g)
TSV_COLUMNS = 4
# Minimum columns to parse (for backwards compatibility with old 3-column format)
TSV_MIN_COLUMNS = 3

# Default graph settings
DEFAULT_GRAPH_DAYS = 14


def ensure_data_dir() -> None:
    """Create data directory if it doesn't exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def append_drink(timestamp: str, drink: str, caffeine_mg: int, sugar_g: int) -> None:
    """Append a drink entry to the TSV log. Creates file with header if needed."""
    ensure_data_dir()

    # Check if file needs header
    needs_header = not DRINKS_FILE.exists() or DRINKS_FILE.stat().st_size == 0

    with DRINKS_FILE.open("a") as f:
        if needs_header:
            f.write("timestamp\tdrink\tcaffeine_mg\tsugar_g\n")
        f.write(f"{timestamp}\t{drink}\t{caffeine_mg}\t{sugar_g}\n")


def get_today_entries() -> list[tuple[str, str, int, int]]:
    """Read all entries from today. Returns list of (timestamp, drink, caffeine_mg, sugar_g)."""
    if not DRINKS_FILE.exists():
        return []

    today = datetime.now().date().isoformat()
    entries: list[tuple[str, str, int, int]] = []

    with DRINKS_FILE.open() as f:
        # Skip header line
        header = next(f, None)
        if header is None:
            return []

        for line in f:
            parts = line.strip().split("\t")
            if len(parts) >= TSV_MIN_COLUMNS and parts[0].startswith(today):
                try:
                    caffeine_mg = int(parts[2])
                    # Support old format (3 columns) and new format (4 columns)
                    sugar_g = int(parts[3]) if len(parts) >= TSV_COLUMNS else 0
                    entries.append((parts[0], parts[1], caffeine_mg, sugar_g))
                except ValueError:
                    # Skip corrupted rows with non-integer values
                    continue

    return entries


def get_today_total() -> tuple[int, int]:
    """Calculate today's total caffeine and sugar intake. Returns (caffeine_mg, sugar_g)."""
    entries = get_today_entries()
    caffeine = sum(mg for _, _, mg, _ in entries)
    sugar = sum(sg for _, _, _, sg in entries)
    return caffeine, sugar


def get_yesterday_date() -> str:
    """Get yesterday's date in ISO format (YYYY-MM-DD)."""
    yesterday = datetime.now().date() - timedelta(days=1)
    return yesterday.isoformat()


def get_yesterday_entries() -> list[tuple[str, str, int, int]]:
    """Read all entries from yesterday. Returns list of (timestamp, drink, caffeine_mg, sugar_g)."""
    if not DRINKS_FILE.exists():
        return []

    yesterday = get_yesterday_date()
    entries: list[tuple[str, str, int, int]] = []

    with DRINKS_FILE.open() as f:
        header = next(f, None)
        if header is None:
            return []

        for line in f:
            parts = line.strip().split("\t")
            if len(parts) >= TSV_MIN_COLUMNS and parts[0].startswith(yesterday):
                try:
                    caffeine_mg = int(parts[2])
                    sugar_g = int(parts[3]) if len(parts) >= TSV_COLUMNS else 0
                    entries.append((parts[0], parts[1], caffeine_mg, sugar_g))
                except ValueError:
                    continue

    return entries


def get_yesterday_total() -> tuple[int, int]:
    """Calculate yesterday's total caffeine and sugar intake. Returns (caffeine_mg, sugar_g)."""
    entries = get_yesterday_entries()
    caffeine = sum(mg for _, _, mg, _ in entries)
    sugar = sum(sg for _, _, _, sg in entries)
    return caffeine, sugar


def get_yesterday_total_by_time(hour: int, minute: int) -> tuple[int, int]:
    """
    Calculate yesterday's caffeine and sugar total up to a specific time.

    Args:
        hour: Hour (0-23)
        minute: Minute (0-59)

    Returns:
        Tuple of (caffeine_mg, sugar_g) consumed yesterday before or at the specified time
    """
    cutoff_time = f"{hour:02d}:{minute:02d}"
    caffeine_total = 0
    sugar_total = 0

    for timestamp, _, mg, sg in get_yesterday_entries():
        if "T" in timestamp:
            time_part = timestamp.split("T")[1][:5]
            if time_part <= cutoff_time:
                caffeine_total += mg
                sugar_total += sg

    return caffeine_total, sugar_total


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


def get_all_entries() -> list[tuple[str, str, int, int]]:
    """
    Read all entries from drinks.tsv.

    Returns:
        List of (timestamp, drink, caffeine_mg, sugar_g) tuples.
    """
    if not DRINKS_FILE.exists():
        return []

    entries: list[tuple[str, str, int, int]] = []
    with DRINKS_FILE.open() as f:
        header = next(f, None)
        if header is None:
            return []

        for line in f:
            parts = line.strip().split("\t")
            if len(parts) >= TSV_MIN_COLUMNS:
                try:
                    caffeine_mg = int(parts[2])
                    sugar_g = int(parts[3]) if len(parts) >= TSV_COLUMNS else 0
                    entries.append((parts[0], parts[1], caffeine_mg, sugar_g))
                except ValueError:
                    continue
    return entries


def get_daily_totals(days: int) -> list[tuple[str, int, int]]:
    """
    Get daily caffeine and sugar totals for the last N days.

    Args:
        days: Number of days to include in the range.

    Returns:
        List of (date_str, caffeine_mg, sugar_g) sorted by date ascending.
        Only includes days from the first day with data through today.
        Days with no drinks logged show as 0mg/0g.
    """
    # Build date range (oldest to newest)
    today = datetime.now().date()
    date_range = [(today - timedelta(days=i)).isoformat() for i in range(days - 1, -1, -1)]

    # Aggregate by date
    daily_caffeine: dict[str, int] = defaultdict(int)
    daily_sugar: dict[str, int] = defaultdict(int)
    for timestamp, _, mg, sg in get_all_entries():
        date_part = timestamp.split("T")[0] if "T" in timestamp else timestamp[:10]
        daily_caffeine[date_part] += mg
        daily_sugar[date_part] += sg

    # If no data at all, return empty
    if not daily_caffeine:
        return []

    # Build result with zeros for missing days
    result: list[tuple[str, int, int]] = []
    for date in date_range:
        result.append((date, daily_caffeine.get(date, 0), daily_sugar.get(date, 0)))

    # Find first day with data and trim from there
    first_data_idx = None
    for i, (_, mg, _) in enumerate(result):
        if mg > 0:
            first_data_idx = i
            break

    if first_data_idx is not None:
        return result[first_data_idx:]

    return []
