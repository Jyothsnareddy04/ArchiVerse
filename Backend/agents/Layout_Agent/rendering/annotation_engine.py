# =============================================================================
# ANNOTATION ENGINE
# =============================================================================
# Adds dimension annotations and labels to rendered layouts.
# =============================================================================

from state import LayoutState


def generate_annotations(state: LayoutState) -> list:
    """
    Generate annotation data for each space.
    Returns a list of dicts with position, text, etc.
    """
    annotations = []

    for space in state.spaces:
        cx = space.centroid.x
        cy = space.centroid.y
        w = space.width
        h = space.height

        annotations.append({
            "name": space.name,
            "x": cx,
            "y": cy,
            "width": round(w, 1),
            "height": round(h, 1),
            "area": round(space.area, 1),
            "label": f"{space.name.replace('_', ' ').title()}\n{w:.0f}×{h:.0f}",
        })

    return annotations
