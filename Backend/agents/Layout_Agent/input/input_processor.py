# =============================================================================
# INPUT PROCESSOR
# =============================================================================
# Normalises raw user input into the canonical format expected by the pipeline.
# Handles:
#   - "40x60" string → (40.0, 60.0) tuple
#   - unit conversion (meters → feet)
#   - facing validation
#   - default fill for missing fields
# =============================================================================

import re
from typing import Any, Dict, Tuple

UNIT_TO_FEET = {
    "feet": 1.0,
    "ft":   1.0,
    "foot": 1.0,
    "meter":  3.28084,
    "meters": 3.28084,
    "m":      3.28084,
}

VALID_FACING = {"north", "south", "east", "west"}


def normalize_input(user_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert raw user input into a clean, validated dict.

    Returns
    -------
    dict with keys:
        plot        : (width_ft, height_ft)
        plot_area   : float (sq ft)
        facing      : str
        bedrooms    : int
        bathrooms   : int
        road_width  : float
        optional_rooms : list[str]
    """
    # ── Parse plot dimensions ────────────────────────────────────────────
    plot = user_input.get("plot")
    if isinstance(plot, str):
        plot = _parse_plot_string(plot)
    elif isinstance(plot, (list, tuple)):
        plot = (float(plot[0]), float(plot[1]))
    else:
        raise ValueError(f"Cannot parse plot: {plot!r}")

    width, height = plot

    # ── Unit conversion ──────────────────────────────────────────────────
    unit = str(user_input.get("unit", "feet")).lower()
    factor = UNIT_TO_FEET.get(unit, 1.0)
    width  *= factor
    height *= factor

    # ── Facing ───────────────────────────────────────────────────────────
    facing = str(user_input.get("facing", "north")).lower().strip()
    if facing not in VALID_FACING:
        print(f"  [WARN] Invalid facing '{facing}', defaulting to 'north'")
        facing = "north"

    # ── Numeric fields ───────────────────────────────────────────────────
    bedrooms  = max(1, int(user_input.get("bedrooms", 2)))
    bathrooms = max(1, int(user_input.get("bathrooms", 2)))
    road_width = float(user_input.get("road_width", 30))

    # ── Optional rooms ───────────────────────────────────────────────────
    optional_rooms = user_input.get("optional_rooms", [])
    if isinstance(optional_rooms, str):
        optional_rooms = [r.strip() for r in optional_rooms.split(",")]

    result = {
        "plot":           (round(width, 2), round(height, 2)),
        "plot_area":      round(width * height, 2),
        "facing":         facing,
        "bedrooms":       bedrooms,
        "bathrooms":      bathrooms,
        "road_width":     road_width,
        "optional_rooms": optional_rooms,
    }

    print(f"\n{'='*50}")
    print("INPUT NORMALISED")
    print(f"{'='*50}")
    for k, v in result.items():
        print(f"  {k:20s} : {v}")

    return result


def _parse_plot_string(text: str) -> Tuple[float, float]:
    """Parse '40x60', '40 x 60', '40X60' etc."""
    parts = [p for p in re.split(r"[^0-9.]+", text) if p]
    if len(parts) < 2:
        raise ValueError(f"Cannot parse plot string: {text!r}")
    return (float(parts[0]), float(parts[1]))