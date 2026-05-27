# =============================================================================
# TEST PLANNING
# =============================================================================

import sys
import os

_this_dir = os.path.dirname(os.path.abspath(__file__))
_parent = os.path.dirname(_this_dir)
if _parent not in sys.path:
    sys.path.insert(0, _parent)

from shapely.geometry import box
from state import LayoutState, Space
from planning.anchor_engine import AnchorEngine


def test_anchor_placement_east():
    """Test anchor placement for east-facing plot."""
    state = LayoutState(
        plot_width=40, plot_height=60,
        facing="east", bedrooms=3, bathrooms=2,
        optional_rooms=["parking", "backyard"],
    )
    state.plot_polygon = box(0, 0, 40, 60)
    state.buildable_polygon = box(2, 2, 38, 55)

    engine = AnchorEngine()
    engine.place_all_anchors(state)

    assert state.get_space("parking") is not None
    assert state.get_space("staircase") is not None
    assert state.get_space("backyard") is not None

    print("  ✔ Anchor placement (east): parking, staircase, backyard placed")


def test_anchor_placement_north():
    """Test anchor placement for north-facing plot."""
    state = LayoutState(
        plot_width=30, plot_height=40,
        facing="north", bedrooms=2, bathrooms=1,
        optional_rooms=["parking"],
    )
    state.plot_polygon = box(0, 0, 30, 40)
    state.buildable_polygon = box(2, 2, 28, 35)

    engine = AnchorEngine()
    engine.place_all_anchors(state)

    assert state.get_space("parking") is not None
    assert state.get_space("staircase") is not None

    print("  ✔ Anchor placement (north): parking, staircase placed")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  PLANNING TESTS")
    print("=" * 60 + "\n")

    test_anchor_placement_east()
    test_anchor_placement_north()

    print("\n  ✔ All planning tests passed!")
