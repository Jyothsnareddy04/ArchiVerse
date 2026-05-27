# =============================================================================
# INPUT VALIDATION
# =============================================================================

from typing import Dict, Any

VALID_FACING = {"north", "south", "east", "west"}

MIN_PLOT_WIDTH  = 20.0   # feet
MAX_PLOT_WIDTH  = 200.0
MIN_PLOT_HEIGHT = 20.0
MAX_PLOT_HEIGHT = 200.0


def validate_input(data: Dict[str, Any]) -> bool:
    """
    Validate normalised input dictionary.
    Raises ValueError with a descriptive message on failure.
    """
    plot = data.get("plot")
    if not plot or len(plot) != 2:
        raise ValueError("Plot dimensions required as (width, height)")

    w, h = plot
    if w < MIN_PLOT_WIDTH or w > MAX_PLOT_WIDTH:
        raise ValueError(f"Plot width {w} out of range [{MIN_PLOT_WIDTH}, {MAX_PLOT_WIDTH}]")
    if h < MIN_PLOT_HEIGHT or h > MAX_PLOT_HEIGHT:
        raise ValueError(f"Plot height {h} out of range [{MIN_PLOT_HEIGHT}, {MAX_PLOT_HEIGHT}]")

    facing = data.get("facing", "")
    if facing not in VALID_FACING:
        raise ValueError(f"Invalid facing: {facing!r}")

    bedrooms = data.get("bedrooms", 0)
    if bedrooms < 1 or bedrooms > 6:
        raise ValueError(f"Bedrooms must be 1-6, got {bedrooms}")

    bathrooms = data.get("bathrooms", 0)
    if bathrooms < 1 or bathrooms > 6:
        raise ValueError(f"Bathrooms must be 1-6, got {bathrooms}")

    return True