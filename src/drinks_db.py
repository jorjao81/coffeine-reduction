"""Built-in caffeine and sugar database for common drinks."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DrinkInfo:
    """Nutritional information for a drink."""

    caffeine_mg: int
    sugar_g: int


# Caffeine (mg) and sugar (g) content for standard serving sizes
# Sources: USDA, manufacturer data
DRINKS_DB: dict[str, DrinkInfo] = {
    "baly": DrinkInfo(caffeine_mg=60, sugar_g=27),  # 250ml
    "baly 473ml": DrinkInfo(caffeine_mg=114, sugar_g=51),  # 473ml
    "fruki": DrinkInfo(caffeine_mg=30, sugar_g=26),
    "fruki zero": DrinkInfo(caffeine_mg=30, sugar_g=0),
    "pepsi max": DrinkInfo(caffeine_mg=69, sugar_g=0),  # Zero sugar
    "red bull": DrinkInfo(caffeine_mg=80, sugar_g=27),  # 250ml
    "red bull zero": DrinkInfo(caffeine_mg=80, sugar_g=0),  # 250ml, zero sugar
}


def get_drink_info(drink_name: str) -> DrinkInfo | None:
    """Look up drink info. Returns None if not found."""
    return DRINKS_DB.get(drink_name.strip().lower())


def get_caffeine(drink_name: str) -> int | None:
    """Look up caffeine content for a drink. Returns None if not found."""
    info = get_drink_info(drink_name)
    return info.caffeine_mg if info else None


def get_sugar(drink_name: str) -> int | None:
    """Look up sugar content for a drink. Returns None if not found."""
    info = get_drink_info(drink_name)
    return info.sugar_g if info else None
