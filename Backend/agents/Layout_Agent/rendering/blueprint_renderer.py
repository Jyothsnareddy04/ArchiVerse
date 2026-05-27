# =============================================================================
# BLUEPRINT RENDERER
# =============================================================================
# Generates a cleaner, technical blueprint-style rendering.
# =============================================================================

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import os
from state import LayoutState


def render_blueprint(
    state: LayoutState,
    output_path: str = None,
) -> str:
    """Render a technical blueprint of the layout."""
    fig, ax = plt.subplots(1, 1, figsize=(12, 14))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("#FAFAFA")

    # Plot boundary
    if state.plot_polygon:
        x, y = state.plot_polygon.exterior.xy
        ax.plot(x, y, color="red", linewidth=2, linestyle="--")

    # Buildable boundary
    if state.buildable_polygon:
        x, y = state.buildable_polygon.exterior.xy
        ax.plot(x, y, color="blue", linewidth=1.5)

    # Rooms
    for space in state.spaces:
        if space.polygon is None or space.polygon.is_empty:
            continue
        if not hasattr(space.polygon, 'exterior') or space.polygon.exterior is None:
            continue
        if space.polygon.area < 0.5:
            continue
        x, y = space.polygon.exterior.xy
        ax.fill(x, y, alpha=0.15, edgecolor="black", linewidth=1.5)

        cx = space.centroid.x
        cy = space.centroid.y
        label = f"{space.name.replace('_', ' ').title()}\n{space.width:.0f}x{space.height:.0f}"
        ax.text(cx, cy, label, ha="center", va="center", fontsize=7, fontweight="bold")

    ax.set_aspect("equal")
    ax.set_title(f"Blueprint - {state.plot_width}x{state.plot_height}ft {state.facing.capitalize()}-facing",
                 fontsize=14)
    ax.set_xlabel("feet")
    ax.set_ylabel("feet")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    if output_path is None:
        out_dir = os.path.join(os.path.dirname(__file__), "..", "output")
        os.makedirs(out_dir, exist_ok=True)
        output_path = os.path.join(out_dir, "blueprint.png")

    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  [BLUEPRINT] Saved to {output_path}")
    return output_path
