# =============================================================================
# TEST PIPELINE – comprehensive integration tests
# =============================================================================

import sys
import os

_this_dir = os.path.dirname(os.path.abspath(__file__))
_parent = os.path.dirname(_this_dir)
if _parent not in sys.path:
    sys.path.insert(0, _parent)

from pipeline import run_pipeline


def test_east_facing_3bhk():
    """Test standard 3BHK east-facing plot."""
    print("\n" + "=" * 60)
    print("TEST: East-facing 3BHK (40x60)")
    print("=" * 60)

    inp = {
        "plot": "40x60",
        "unit": "feet",
        "facing": "east",
        "bedrooms": 3,
        "bathrooms": 2,
        "optional_rooms": ["parking", "dining", "store", "backyard"],
    }

    state = run_pipeline(inp, render=False)

    assert len(state.spaces) >= 5, f"Expected >= 5 spaces, got {len(state.spaces)}"
    assert state.get_space("living") is not None, "Missing living room"
    assert state.get_space("kitchen") is not None, "Missing kitchen"
    assert state.get_space("master_bedroom") is not None, "Missing master bedroom"
    assert state.utilisation > 0.4, f"Low utilisation: {state.utilisation}"

    print(f"\n  ✔ PASSED – {len(state.spaces)} spaces, util={state.utilisation*100:.1f}%")


def test_north_facing_2bhk():
    """Test 2BHK north-facing plot."""
    print("\n" + "=" * 60)
    print("TEST: North-facing 2BHK (30x40)")
    print("=" * 60)

    inp = {
        "plot": (30, 40),
        "unit": "feet",
        "facing": "north",
        "bedrooms": 2,
        "bathrooms": 2,
        "optional_rooms": ["parking", "dining"],
    }

    state = run_pipeline(inp, render=False)

    assert state.get_space("living") is not None
    assert state.get_space("kitchen") is not None
    assert state.utilisation > 0.3

    print(f"\n  ✔ PASSED – {len(state.spaces)} spaces")


def test_south_facing_4bhk():
    """Test larger 4BHK south-facing plot."""
    print("\n" + "=" * 60)
    print("TEST: South-facing 4BHK (50x80)")
    print("=" * 60)

    inp = {
        "plot": "50x80",
        "facing": "south",
        "bedrooms": 4,
        "bathrooms": 3,
        "optional_rooms": ["parking", "dining", "store", "backyard"],
    }

    state = run_pipeline(inp, render=False)

    assert state.get_space("living") is not None
    assert state.get_space("kitchen") is not None

    print(f"\n  ✔ PASSED – {len(state.spaces)} spaces")


def test_west_facing_2bhk():
    """Test west-facing 2BHK."""
    print("\n" + "=" * 60)
    print("TEST: West-facing 2BHK (30x50)")
    print("=" * 60)

    inp = {
        "plot": "30x50",
        "facing": "west",
        "bedrooms": 2,
        "bathrooms": 1,
        "optional_rooms": ["parking"],
    }

    state = run_pipeline(inp, render=False)

    assert state.get_space("living") is not None
    assert state.get_space("kitchen") is not None

    print(f"\n  ✔ PASSED – {len(state.spaces)} spaces")


def test_minimal_plot():
    """Test minimum viable plot."""
    print("\n" + "=" * 60)
    print("TEST: Minimal plot (25x30)")
    print("=" * 60)

    inp = {
        "plot": "25x30",
        "facing": "north",
        "bedrooms": 1,
        "bathrooms": 1,
        "optional_rooms": [],
    }

    state = run_pipeline(inp, render=False)

    assert state.get_space("living") is not None
    assert state.get_space("kitchen") is not None

    print(f"\n  ✔ PASSED – {len(state.spaces)} spaces")


if __name__ == "__main__":
    print("\n" + "▓" * 60)
    print("  ARCHIVERSE TEST SUITE")
    print("▓" * 60)

    tests = [
        test_east_facing_3bhk,
        test_north_facing_2bhk,
        test_south_facing_4bhk,
        test_west_facing_2bhk,
        test_minimal_plot,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"\n  ❌ FAILED: {e}")
            import traceback
            traceback.print_exc()

    print(f"\n{'='*60}")
    print(f"  RESULTS: {passed}/{passed + failed} passed")
    print(f"{'='*60}")
