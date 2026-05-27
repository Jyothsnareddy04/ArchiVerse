# =============================================================================
# TEST RULES
# =============================================================================

import sys
import os

_this_dir = os.path.dirname(os.path.abspath(__file__))
_parent = os.path.dirname(_this_dir)
if _parent not in sys.path:
    sys.path.insert(0, _parent)

from config.ghmc_rules import GHMC
from config.room_standards import ROOM_STANDARDS
from rules.room_rules import get_min_dimensions, validate_room_size


def test_ghmc_setbacks():
    """Test GHMC setback calculation."""
    setbacks = GHMC.setbacks(150, "east")
    assert "north" in setbacks
    assert "south" in setbacks
    assert "east" in setbacks
    assert "west" in setbacks
    assert setbacks["east"] > setbacks["west"]  # East is front (road side)
    print(f"  ✔ GHMC setbacks: {setbacks}")


def test_room_standards():
    """Test room standards are defined."""
    assert "master_bedroom" in ROOM_STANDARDS
    assert ROOM_STANDARDS["master_bedroom"]["min_width"] >= 12
    print("  ✔ Room standards: master_bedroom minimum width OK")


def test_room_validation():
    """Test room size validation."""
    assert validate_room_size("bedroom", 11, 12) == True
    assert validate_room_size("bedroom", 5, 5) == False
    print("  ✔ Room validation: correct")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  RULES TESTS")
    print("=" * 60 + "\n")

    test_ghmc_setbacks()
    test_room_standards()
    test_room_validation()

    print("\n  ✔ All rules tests passed!")
