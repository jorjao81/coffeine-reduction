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


def log_drink(drink_name: str, mg: int | None = None, sugar: int | None = None) -> tuple[str, int, int, int, int]:
    """
    Log a drink and return (drink_name, caffeine_mg, sugar_g, today_caffeine, today_sugar).

    Args:
        drink_name: Name of the drink to log.
        mg: Optional caffeine override in milligrams. If provided, uses this value.
            If None and drink is known, uses database value.
            If None and drink is unknown, raises ValueError.
        sugar: Optional sugar override in grams. If provided, uses this value.
            If None and drink is known, uses database value.
            If None and drink is unknown, defaults to 0.

    Raises:
        ValueError: If drink name is invalid, mg/sugar is negative, or drink is unknown without mg.
    """
    normalized_name = validate_drink_name(drink_name)

    # Validate mg if provided
    if mg is not None and mg < 0:
        msg = "Caffeine amount cannot be negative."
        raise ValueError(msg)

    if sugar is not None and sugar < 0:
        msg = "Sugar amount cannot be negative."
        raise ValueError(msg)

    # Look up drink info
    drink_info = drinks_db.get_drink_info(normalized_name)

    # Determine caffeine amount: use mg override if provided, otherwise lookup
    if mg is not None:
        caffeine = mg
    elif drink_info is not None:
        caffeine = drink_info.caffeine_mg
    else:
        msg = f"Unknown drink: {normalized_name}. Use --mg to specify caffeine amount."
        raise ValueError(msg)

    # Determine sugar amount: use sugar override if provided, otherwise lookup, default to 0
    if sugar is not None:
        sugar_g = sugar
    elif drink_info is not None:
        sugar_g = drink_info.sugar_g
    else:
        sugar_g = 0

    timestamp = datetime.now().isoformat(timespec="seconds")
    data.append_drink(timestamp, normalized_name, caffeine, sugar_g)
    today_caffeine, today_sugar = data.get_today_total()

    return (normalized_name, caffeine, sugar_g, today_caffeine, today_sugar)
