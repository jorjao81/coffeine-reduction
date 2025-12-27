"""Drink logging business logic."""

from __future__ import annotations

from datetime import datetime

from src import data, drinks_db


def validate_drink_name(drink_name: str) -> str:
    """
    Validate and normalize drink name.

    Raises ValueError if name contains invalid characters.
    Returns stripped, lowercase name.
    """
    normalized = drink_name.strip().lower()

    if not normalized:
        msg = "Drink name cannot be empty."
        raise ValueError(msg)

    # Tabs and newlines would corrupt TSV format
    if "\t" in normalized or "\n" in normalized or "\r" in normalized:
        msg = "Drink name cannot contain tabs or newlines."
        raise ValueError(msg)

    return normalized


def log_drink(drink_name: str, mg: int | None = None) -> tuple[str, int, int]:
    """
    Log a drink and return (drink_name, caffeine_mg, today_total).

    Args:
        drink_name: Name of the drink to log.
        mg: Optional caffeine override in milligrams. If provided, uses this value.
            If None and drink is known, uses database value.
            If None and drink is unknown, raises ValueError.

    Raises:
        ValueError: If drink name is invalid, mg is negative, or drink is unknown without mg.
    """
    normalized_name = validate_drink_name(drink_name)

    # Validate mg if provided
    if mg is not None and mg < 0:
        msg = "Caffeine amount cannot be negative."
        raise ValueError(msg)

    # Determine caffeine amount: use mg override if provided, otherwise lookup
    if mg is not None:
        caffeine = mg
    else:
        caffeine = drinks_db.get_caffeine(normalized_name)
        if caffeine is None:
            msg = f"Unknown drink: {normalized_name}. Use --mg to specify caffeine amount."
            raise ValueError(msg)

    timestamp = datetime.now().isoformat(timespec="seconds")
    data.append_drink(timestamp, normalized_name, caffeine)
    today_total = data.get_today_total()

    return (normalized_name, caffeine, today_total)
