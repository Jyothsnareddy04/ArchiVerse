# =============================================================================
# EXPORT ENGINE
# =============================================================================

import json
import os
from state import LayoutState


def export_to_json(state: LayoutState, output_path: str = None) -> str:
    """Export the layout to a JSON file."""
    data = {
        "plot": {
            "width": state.plot_width,
            "height": state.plot_height,
            "facing": state.facing,
        },
        "rooms": [],
        "score": state.score,
        "utilisation": round(state.utilisation * 100, 1),
        "errors": state.errors,
        "warnings": state.warnings,
    }

    for space in state.spaces:
        minx, miny, maxx, maxy = space.polygon.bounds
        data["rooms"].append({
            "name": space.name,
            "type": space.room_type,
            "zone": space.zone,
            "x": round(minx, 2),
            "y": round(miny, 2),
            "width": round(space.width, 2),
            "height": round(space.height, 2),
            "area": round(space.area, 2),
        })

    if output_path is None:
        out_dir = os.path.join(os.path.dirname(__file__), "..", "output")
        os.makedirs(out_dir, exist_ok=True)
        output_path = os.path.join(out_dir, "layout.json")

    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)

    print(f"  [EXPORT] JSON saved to {output_path}")
    return output_path
