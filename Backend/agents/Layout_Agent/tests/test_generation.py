# =============================================================================
# TEST GENERATION – end-to-end layout generation tests
# =============================================================================

import sys
import os

_this_dir = os.path.dirname(os.path.abspath(__file__))
_parent = os.path.dirname(_this_dir)
if _parent not in sys.path:
    sys.path.insert(0, _parent)

from pipeline import run_pipeline


def test_generate_and_render():
    """Full generation with rendering."""
    inp = {
        "plot": "40x60",
        "facing": "east",
        "bedrooms": 3,
        "bathrooms": 2,
        "optional_rooms": ["parking", "dining", "store", "backyard"],
    }

    state = run_pipeline(inp, render=True)

    # Check output files
    out_dir = os.path.join(_parent, "output")
    assert os.path.exists(os.path.join(out_dir, "layout.png")), "layout.png not generated"
    assert os.path.exists(os.path.join(out_dir, "blueprint.png")), "blueprint.png not generated"
    assert os.path.exists(os.path.join(out_dir, "layout.json")), "layout.json not generated"

    print("  ✔ Generation test passed – all outputs created")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  GENERATION TESTS")
    print("=" * 60 + "\n")

    test_generate_and_render()
