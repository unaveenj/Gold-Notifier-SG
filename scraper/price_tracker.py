"""
price_tracker.py — Lightweight utility for gold price change tracking.

Provides:
  - load_previous_prices()       : read price.json from disk
  - save_prices()                : write price.json to disk
  - calculate_percentage_change(): safe % change computation
  - format_change()              : human-readable change string with arrow
"""

import json
from pathlib import Path

PRICE_FILE = Path(__file__).parent / "price.json"


def load_previous_prices(path: Path = PRICE_FILE) -> dict:
    """
    Load previously stored prices from a JSON file.

    Returns an empty dict on the first run (file not found) or if the
    file is malformed — callers treat {} as "no previous data".

    Expected file format:
        {
          "916": <last_price_as_number_or_string>,
          "999": <last_price_as_number_or_string>
        }
    """
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_prices(prices: dict, path: Path = PRICE_FILE) -> None:
    """
    Persist current prices to a local JSON file.

    Args:
        prices: dict with keys "916" and "999" mapping to current prices.
        path:   destination file path (defaults to price.json beside this module).
    """
    with open(path, "w") as f:
        json.dump(prices, f, indent=2)


def calculate_percentage_change(current, previous) -> float | None:
    """
    Compute percentage change between two price values.

    Returns:
        float  — percentage change (can be negative)
        None   — when either value is missing, non-numeric, or previous == 0
    """
    try:
        cur  = float(current)
        prev = float(previous)
        if prev == 0:
            return None
        return ((cur - prev) / prev) * 100
    except (TypeError, ValueError):
        return None


def format_change(pct_change: float | None) -> str:
    """
    Format a percentage change value into a display string.

    Rules:
        - None input           → "" (first run, no previous data)
        - abs(change) < 0.20%  → "↔ No significant change"
        - positive change      → "📈 +X.XX% since last update"
        - negative change      → "📉 -X.XX% since last update"

    Returns an empty string when there is nothing meaningful to show,
    so callers can safely skip adding a line break.
    """
    if pct_change is None:
        return ""
    if abs(pct_change) < 0.20:
        return "↔ No significant change"
    arrow = "📈" if pct_change > 0 else "📉"
    sign  = "+" if pct_change > 0 else ""
    return f"{arrow} {sign}{pct_change:.2f}% since last update"
