# =============================================================================
# TEST GEOMETRY
# =============================================================================

import sys
import os

_this_dir = os.path.dirname(os.path.abspath(__file__))
_parent = os.path.dirname(_this_dir)
if _parent not in sys.path:
    sys.path.insert(0, _parent)

from shapely.geometry import box
from geometry.boundary_manager import create_plot_boundary, create_buildable_boundary
from geometry.polygon_manager import create_rectangle, subtract_polygon, polygon_overlap_area
from geometry.subtraction_engine import SubtractionEngine
from geometry.collision_engine import check_all_overlaps
from state import Space


def test_plot_boundary():
    """Test plot polygon creation."""
    poly = create_plot_boundary(40, 60)
    assert abs(poly.area - 2400) < 0.1
    print("  ✔ plot_boundary: correct area")


def test_buildable_boundary():
    """Test setback application."""
    plot = create_plot_boundary(40, 60)
    buildable, setbacks = create_buildable_boundary(plot, "east")
    assert buildable.area < plot.area
    assert buildable.area > 0
    print(f"  ✔ buildable_boundary: {buildable.area:.1f} sqft (< {plot.area:.1f})")


def test_subtraction():
    """Test polygon subtraction."""
    base = box(0, 0, 40, 60)
    cut = box(0, 0, 10, 10)
    result = subtract_polygon(base, cut)
    assert abs(result.area - (2400 - 100)) < 1
    print("  ✔ subtraction: correct remaining area")


def test_subtraction_engine():
    """Test the SubtractionEngine class."""
    buildable = box(0, 0, 40, 60)
    engine = SubtractionEngine(buildable)

    room1 = box(0, 0, 15, 20)
    engine.subtract("room1", room1)
    assert engine.remaining_area < 2400

    room2 = box(15, 0, 30, 15)
    engine.subtract("room2", room2)
    assert engine.remaining_area < (2400 - 300 - 225)

    print(f"  ✔ subtraction_engine: remaining={engine.remaining_area:.1f}")


def test_overlap_detection():
    """Test overlap detection."""
    a = Space("a", "bedroom", box(0, 0, 10, 10))
    b = Space("b", "bedroom", box(5, 5, 15, 15))
    c = Space("c", "bathroom", box(20, 20, 25, 27))

    overlaps = check_all_overlaps([a, b, c], tolerance=0.5)
    assert len(overlaps) == 1
    assert overlaps[0][0] == "a" and overlaps[0][1] == "b"
    print(f"  ✔ overlap_detection: found {len(overlaps)} overlap")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  GEOMETRY TESTS")
    print("=" * 60 + "\n")

    test_plot_boundary()
    test_buildable_boundary()
    test_subtraction()
    test_subtraction_engine()
    test_overlap_detection()

    print("\n  ✔ All geometry tests passed!")
