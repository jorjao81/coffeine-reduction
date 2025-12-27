"""Built-in caffeine database for common drinks."""

from __future__ import annotations

# Caffeine content in mg (standard serving sizes)
# Sources: USDA, manufacturer data
DRINKS_DB: dict[str, int] = {
    # Espresso-based drinks
    "espresso": 63,  # 1 shot
    "double espresso": 126,
    "ristretto": 63,
    "lungo": 80,
    # Brewed coffee
    "coffee": 95,  # 8 oz brewed
    "drip coffee": 95,
    "french press": 107,
    "cold brew": 200,
    "pour over": 95,
    # Milk-based espresso drinks
    "latte": 75,
    "cappuccino": 75,
    "flat white": 130,
    "americano": 95,
    "mocha": 95,
    "macchiato": 75,
    "cortado": 63,
    # Tea
    "tea": 47,
    "black tea": 47,
    "green tea": 28,
    "white tea": 15,
    "oolong tea": 37,
    "matcha": 70,
    "chai": 50,
    "earl grey": 47,
    "english breakfast": 47,
    # Soft drinks
    "cola": 34,
    "diet cola": 46,
    "pepsi": 38,
    "diet pepsi": 35,
    "dr pepper": 41,
    "mountain dew": 54,
    # Energy drinks
    "energy drink": 80,
    "red bull": 80,
    "monster": 160,
    "rockstar": 160,
    "bang": 300,
    "celsius": 200,
    "5-hour energy": 200,
    # Other
    "hot chocolate": 5,
    "decaf coffee": 2,
    "decaf espresso": 3,
}


def get_caffeine(drink_name: str) -> int | None:
    """Look up caffeine content for a drink. Returns None if not found."""
    return DRINKS_DB.get(drink_name.strip().lower())
