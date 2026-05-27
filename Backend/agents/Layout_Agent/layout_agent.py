# =============================================================================
# ARCHIVERSE — PRODUCTION LAYOUT AGENT
# =============================================================================
# Full topology-aware residential layout generation engine
#
# PIPELINE:
#
# INPUT
#   ↓
# RULE ENGINE
#   ↓
# LLM SIZE / TOPOLOGY REASONING
#   ↓
# GNN ZONING
#   ↓
# TOPOLOGY SUBTRACTION SOLVER
#   ↓
# VALIDATION
#   ↓
# WALL GENERATION
#   ↓
# RENDER
#
# IMPORTANT:
# This is NOT rectangle placement.
#
# This is:
# architectural topology generation
# =============================================================================

import os
import sys

# =============================================================================
# UTF FIX
# =============================================================================

if sys.platform == "win32":

    sys.stdout.reconfigure(
        encoding="utf-8",
        errors="replace"
    )

    sys.stderr.reconfigure(
        encoding="utf-8",
        errors="replace"
    )

# =============================================================================
# PATH
# =============================================================================

THIS_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

if THIS_DIR not in sys.path:

    sys.path.insert(
        0,
        THIS_DIR
    )

# =============================================================================
# IMPORTS
# =============================================================================

from pipeline import run_pipeline

# =============================================================================
# SAMPLE INPUT
# =============================================================================

SAMPLE_INPUT = {

    # =====================================================
    # PLOT
    # =====================================================

    "plot_width": 40,

    "plot_height": 60,

    "unit": "feet",

    # =====================================================
    # ROAD
    # =====================================================

    "facing": "north",

    "road_width": 30,

    # =====================================================
    # HOUSE
    # =====================================================

    "house_type": "individual",

    # =====================================================
    # PROGRAM
    # =====================================================

    "bedrooms": 3,

    "bathrooms": 2,

    # =====================================================
    # OPTIONAL
    # =====================================================

    "optional_rooms": [

        "dining",

        "store",

        "backyard"
    ],

    # =====================================================
    # OPEN SPACE
    # =====================================================

    "parking": True,

    "lawn": True,

    "plants": True,

    # =====================================================
    # STYLE
    # =====================================================

    "style": "modern"
}

# =============================================================================
# MAIN
# =============================================================================


def main():

    print("\n" + "=" * 70)

    print(" ARCHIVERSE — TOPOLOGY LAYOUT AGENT ")

    print("=" * 70)

    print(

        "\nPIPELINE:"

        "\n  INPUT"

        "\n    ↓"

        "\n  RULE ENGINE"

        "\n    ↓"

        "\n  LLM REASONER"

        "\n    ↓"

        "\n  GNN ZONING"

        "\n    ↓"

        "\n  TOPOLOGY SUBTRACTION SOLVER"

        "\n    ↓"

        "\n  VALIDATION"

        "\n    ↓"

        "\n  WALL GENERATION"

        "\n    ↓"

        "\n  RENDER"
    )

    # =====================================================
    # RUN
    # =====================================================

    variants = run_pipeline(

        SAMPLE_INPUT,

        render=True
    )

    # =====================================================
    # RESULTS
    # =====================================================

    print("\n" + "=" * 70)

    print(" GENERATED VARIANTS ")

    print("=" * 70)

    for idx, state in enumerate(variants):

        print(
            f"\n\nVARIANT {idx + 1}"
        )

        print("-" * 60)

        total = 0

        for s in state.spaces:

            total += s.area

            print(

                f"{s.name:25s}"

                f"{s.width:7.1f} x"

                f"{s.height:7.1f}"

                f"  |"

                f"  {s.area:8.1f} sqft"
            )

        print("-" * 60)

        print(
            f"TOTAL BUILT AREA :"
            f" {total:.1f} sqft"
        )

        # =================================================
        # VALIDATION
        # =================================================

        if hasattr(state, "validation"):

            val = state.validation

            print("\nVALIDATION")

            print(
                f"  valid : {val.get('valid', False)}"
            )

            print(
                f"  overlaps : "
                f"{len(val.get('overlaps', []))}"
            )

            print(
                f"  plumbing : "
                f"{len(val.get('plumbing_issues', []))}"
            )

            print(
                f"  ventilation : "
                f"{len(val.get('ventilation_issues', []))}"
            )

        # =================================================
        # TOPOLOGY SCORE
        # =================================================

        if hasattr(state, "topology_score"):

            score = state.topology_score

            print("\nTOPOLOGY SCORE")

            print(
                f"  score : "
                f"{score.get('score', 0)}"
            )

            print(
                f"  compactness : "
                f"{score.get('avg_compactness', 0)}"
            )

            print(
                f"  deadspace : "
                f"{score.get('deadspace_percent', 0)}%"
            )

    print("\n" + "=" * 70)

    print(" OUTPUT GENERATED ")

    print("=" * 70)

    print(

        "\nCheck output folder for:"

        "\n  • rendered layouts"

        "\n  • topology visualizations"

        "\n  • wall drawings"

        "\n  • validation overlays"
    )

# =============================================================================
# ENTRY
# =============================================================================

if __name__ == "__main__":

    main()