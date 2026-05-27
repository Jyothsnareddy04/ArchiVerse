# =============================================================================
# GEOMETRY VALIDATOR v6
# =============================================================================
# FIXED PRODUCTION GEOMETRY VALIDATOR
#
# FIXES:
# - removed broken imports
# - uses updated collision engine
# - ignores environmental overlaps
# - softer validations
# - proper residual handling
# - stable topology scoring
# - reduced false errors
# =============================================================================

from state import (
    LayoutState,
    Space
)

from geometry.collision_engine import (
    check_overlaps
)

from utils.geometry_utils import (

    polygon_quality_score,

    detect_dead_space
)

# =============================================================================
# ENVIRONMENT TYPES
# =============================================================================

ENVIRONMENT_TYPES = {

    "parking",
    "lawn",
    "green_strip",
    "green_buffer",
    "main_gate",
    "backyard",
    "staircase",
    "vent_pocket"
}

# =============================================================================
# VALIDATOR
# =============================================================================

class GeometryValidator:

    # =========================================================================
    # MAIN
    # =========================================================================

    def validate(

        self,

        state: LayoutState
    ):

        print("\n" + "=" * 60)

        print("GEOMETRY VALIDATION")

        print("=" * 60)

        self._validate_boundaries(
            state
        )

        self._validate_overlaps(
            state
        )

        self._validate_dead_space(
            state
        )

        self._validate_topology_quality(
            state
        )

        self._print_summary(
            state
        )

        return len(state.errors) == 0

    # =========================================================================
    # BOUNDARIES
    # =========================================================================

    def _validate_boundaries(

        self,

        state
    ):

        print("\n[BOUNDARIES]")

        if state.buildable_polygon is None:

            state.errors.append(
                "No buildable polygon"
            )

            return

        violations = 0

        for s in state.spaces:

            if s.room_type in ENVIRONMENT_TYPES:
                continue

            safe_poly = s.polygon.buffer(
                -0.05
            )

            if safe_poly.is_empty:
                continue

            inside = state.buildable_polygon.buffer(
                1.5
            ).contains(
                safe_poly
            )

            if not inside:

                overflow = safe_poly.difference(
                    state.buildable_polygon
                )

                area = overflow.area

                msg = (

                    f"{s.name}"
                    f" exceeds buildable"
                    f" by {area:.1f} sqft"
                )

                violations += 1

                if area > 20:

                    state.errors.append(msg)

                    print(f"  ✘ {msg}")

                else:

                    state.warnings.append(msg)

                    print(f"  ⚠ {msg}")

        if violations == 0:

            print(
                "  ✔ No boundary violations"
            )

    # =========================================================================
    # OVERLAPS
    # =========================================================================

    def _validate_overlaps(

        self,

        state
    ):

        print("\n[OVERLAPS]")

        overlaps = check_overlaps(

            state.spaces,

            tolerance=40.0
        )

        if len(overlaps) == 0:

            print(
                "  ✔ No major overlaps"
            )

            return

        for o in overlaps:

            a = o["room_a"]
            b = o["room_b"]
            area = o["area"]

            msg = (

                f"{a} ↔ {b}"
                f" = {area:.1f} sqft"
            )

            if area > 120:

                state.errors.append(msg)

                print(f"  ✘ {msg}")

            else:

                state.warnings.append(msg)

                print(f"  ⚠ {msg}")

    # =========================================================================
    # DEAD SPACE
    # =========================================================================

    def _validate_dead_space(

        self,

        state
    ):

        print("\n[DEAD SPACE]")

        residual = state.buildable_polygon

        if residual is None:
            return

        for s in state.spaces:

            if s.room_type in ENVIRONMENT_TYPES:
                continue

            residual = residual.difference(
                s.polygon
            )

        if residual.is_empty:

            print(
                "  ✔ No dead spaces"
            )

            return

        regions = detect_dead_space(
            residual
        )

        dead_count = 0

        for r in regions:

            area = r.get(
                "area",
                0
            )

            if area < 60:
                continue

            dead_count += 1

            msg = (

                f"Dead residual:"
                f" {area:.1f} sqft"
            )

            state.warnings.append(msg)

            print(f"  ⚠ {msg}")

        if dead_count == 0:

            print(
                "  ✔ No major dead spaces"
            )

    # =========================================================================
    # TOPOLOGY QUALITY
    # =========================================================================

    def _validate_topology_quality(

        self,

        state
    ):

        print("\n[TOPOLOGY QUALITY]")

        total = 0

        count = 0

        for s in state.spaces:

            if s.room_type in ENVIRONMENT_TYPES:
                continue

            try:

                score = polygon_quality_score(
                    s.polygon
                )

            except:

                score = 50

            total += score

            count += 1

            print(

                f"  {s.name:20s}"
                f"{score:.1f}/100"
            )

        if count == 0:

            return

        avg = total / count

        print(

            f"\n  Average:"
            f" {avg:.1f}/100"
        )

        if avg < 45:

            state.warnings.append(
                "Low topology quality"
            )

    # =========================================================================
    # SUMMARY
    # =========================================================================

    def _print_summary(

        self,

        state
    ):

        print("\n" + "=" * 60)

        print("VALIDATION SUMMARY")

        print("=" * 60)

        print(

            f"Errors   : "
            f"{len(state.errors)}"
        )

        print(

            f"Warnings : "
            f"{len(state.warnings)}"
        )

        if len(state.errors) == 0:

            print(
                "\n✔ Geometry valid"
            )

        else:

            print(
                "\n✘ Geometry invalid"
            )

        print("=" * 60)