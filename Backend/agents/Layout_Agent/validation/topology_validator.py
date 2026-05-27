# =============================================================================
# TOPOLOGY VALIDATOR v21
# =============================================================================
# PURE TOPOLOGY VALIDATION ENGINE
#
# FIXES
#
# ✔ duplicate validation
# ✔ outdoor overlap false positives
# ✔ living false failures
# ✔ staircase corner checks
# ✔ utility outdoor checks
# ✔ invalid geometry crashes
# ✔ buildable containment corruption
# ✔ residual scoring instability
#
# =============================================================================

from shapely.geometry import (
    Polygon,
    MultiPolygon
)

from shapely.ops import unary_union

from state import LayoutState

# =============================================================================
# CONSTANTS
# =============================================================================

OUTDOOR_TYPES = {

    "green_strip",
    "front_lawn",
    "main_gate",
    "parking",
    "backyard",
    "staircase"
}

INDOOR_TYPES = {

    "living",
    "dining",
    "kitchen",
    "master_bedroom",
    "bedroom",
    "bathroom",
    "wash_area",
    "store",
    "utility"
}

MAX_OVERLAP_AREA = 8.0

MIN_EXTERIOR_TOUCH = 2.0

# =============================================================================
# ENGINE
# =============================================================================

class TopologyValidator:

    # =========================================================================
    # MAIN
    # =========================================================================

    def validate(

        self,

        state: LayoutState
    ):

        print("\n" + "=" * 60)
        print("TOPOLOGY VALIDATOR v21")
        print("=" * 60)

        state.errors = []
        state.warnings = []

        # ---------------------------------------------------------------------
        # CLEAN
        # ---------------------------------------------------------------------

        self._remove_duplicates(
            state
        )

        self._remove_invalid_spaces(
            state
        )

        # ---------------------------------------------------------------------
        # OVERLAPS
        # ---------------------------------------------------------------------

        overlap = self._validate_overlaps(
            state
        )

        # ---------------------------------------------------------------------
        # CONTAINMENT
        # ---------------------------------------------------------------------

        containment = self._validate_containment(
            state
        )

        # ---------------------------------------------------------------------
        # PARKING
        # ---------------------------------------------------------------------

        self._validate_parking(
            state
        )

        # ---------------------------------------------------------------------
        # STAIR
        # ---------------------------------------------------------------------

        self._validate_staircase(
            state
        )

        # ---------------------------------------------------------------------
        # UTILITY
        # ---------------------------------------------------------------------

        self._validate_utility(
            state
        )

        # ---------------------------------------------------------------------
        # LIVING
        # ---------------------------------------------------------------------

        self._validate_living(
            state
        )

        # ---------------------------------------------------------------------
        # SCORE
        # ---------------------------------------------------------------------

        state.layout_score = (
            self.calculate_score(
                state,
                overlap,
                containment
            )
        )

        print(
            f"\n✔ Score : "
            f"{state.layout_score:.1f}"
        )

        return len(state.errors) == 0

    # =========================================================================
    # REMOVE DUPLICATES
    # =========================================================================

    def _remove_duplicates(

        self,

        state
    ):

        unique = []

        seen = set()

        for s in state.spaces:

            key = (

                s.name,
                round(s.area, 1)
            )

            if key in seen:
                continue

            seen.add(key)

            unique.append(s)

        state.spaces = unique

    # =========================================================================
    # REMOVE INVALID
    # =========================================================================

    def _remove_invalid_spaces(

        self,

        state
    ):

        filtered = []

        for s in state.spaces:

            if s.polygon is None:
                continue

            if s.polygon.is_empty:
                continue

            if s.area < 8:
                continue

            filtered.append(s)

        state.spaces = filtered

    # =========================================================================
    # OVERLAPS
    # =========================================================================

    def _validate_overlaps(

        self,

        state
    ):

        print("\n[OVERLAPS]")

        total = 0.0

        indoor = [

            s for s in state.spaces

            if s.room_type in INDOOR_TYPES
        ]

        for i in range(len(indoor)):

            a = indoor[i]

            for j in range(i + 1, len(indoor)):

                b = indoor[j]

                try:

                    inter = a.polygon.intersection(
                        b.polygon
                    )

                    if inter.is_empty:
                        continue

                    if inter.area <= 1:
                        continue

                    total += inter.area

                except Exception:
                    continue

        print(
            f"  overlap area : "
            f"{total:.1f}"
        )

        if total > MAX_OVERLAP_AREA:

            state.errors.append(
                f"Indoor overlap "
                f"{total:.1f}"
            )

        return total

    # =========================================================================
    # CONTAINMENT
    # =========================================================================

    def _validate_containment(

        self,

        state
    ):

        print("\n[CONTAINMENT]")

        if state.buildable_polygon is None:
            return 0

        issues = 0

        expanded = (
            state.buildable_polygon.buffer(
                0.5
            )
        )

        for s in state.spaces:

            if s.room_type not in INDOOR_TYPES:
                continue

            try:

                if not expanded.contains(
                    s.polygon
                ):

                    issues += 1

            except Exception:

                issues += 1

        print(
            f"  containment : "
            f"{issues}"
        )

        if issues > 0:

            state.warnings.append(
                f"{issues} containment issues"
            )

        return issues

    # =========================================================================
    # PARKING
    # =========================================================================

    def _validate_parking(

        self,

        state
    ):

        print("\n[PARKING]")

        parking = state.get_space(
            "parking"
        )

        if parking is None:
            return

        try:

            boundary = (
                state.plot_polygon.boundary
            )

            shared = (

                parking.polygon.boundary
                .intersection(boundary)
            )

            print(
                f"  boundary touch : "
                f"{shared.length:.1f}"
            )

            if shared.length < 2:

                state.warnings.append(
                    "Parking detached"
                )

        except Exception:

            state.warnings.append(
                "Parking validation failed"
            )

    # =========================================================================
    # STAIRCASE
    # =========================================================================

    def _validate_staircase(

        self,

        state
    ):

        print("\n[STAIRCASE]")

        stair = state.get_space(
            "staircase"
        )

        if stair is None:
            return

        try:

            px0, py0, px1, py1 = (
                state.plot_polygon.bounds
            )

            sx0, sy0, sx1, sy1 = (
                stair.polygon.bounds
            )

            tolerance = 1.2

            corner = any([

                abs(sx0 - px0) < tolerance
                and
                abs(sy0 - py0) < tolerance,

                abs(sx1 - px1) < tolerance
                and
                abs(sy0 - py0) < tolerance,

                abs(sx0 - px0) < tolerance
                and
                abs(sy1 - py1) < tolerance,

                abs(sx1 - px1) < tolerance
                and
                abs(sy1 - py1) < tolerance
            ])

            print(
                f"  corner anchored : "
                f"{corner}"
            )

            if not corner:

                state.warnings.append(
                    "Staircase not corner anchored"
                )

        except Exception:

            state.warnings.append(
                "Stair validation failed"
            )

    # =========================================================================
    # UTILITY
    # =========================================================================

    def _validate_utility(

        self,

        state
    ):

        print("\n[UTILITY]")

        utility = state.get_space(
            "utility"
        )

        kitchen = state.get_space(
            "kitchen"
        )

        if utility is None:
            return

        if kitchen is None:
            return

        try:

            touching = (

                utility.polygon.distance(
                    kitchen.polygon
                ) < 0.6
            )

            print(
                f"  kitchen attached : "
                f"{touching}"
            )

            if not touching:

                state.warnings.append(
                    "Utility detached"
                )

        except Exception:

            state.warnings.append(
                "Utility validation failed"
            )

    # =========================================================================
    # LIVING
    # =========================================================================

    def _validate_living(

        self,

        state
    ):

        print("\n[LIVING]")

        living = state.get_space(
            "living"
        )

        if living is None:

            state.errors.append(
                "Living missing"
            )

            return

        print(
            f"  living area : "
            f"{living.area:.1f}"
        )

        if living.area < 100:

            state.warnings.append(
                "Living too small"
            )

    # =========================================================================
    # SCORE
    # =========================================================================

    def calculate_score(

        self,

        state,

        overlap,

        containment
    ):

        score = 100.0

        # ---------------------------------------------------------------------
        # OVERLAPS
        # ---------------------------------------------------------------------

        score -= overlap * 0.6

        # ---------------------------------------------------------------------
        # CONTAINMENT
        # ---------------------------------------------------------------------

        score -= containment * 3

        # ---------------------------------------------------------------------
        # UTILIZATION
        # ---------------------------------------------------------------------

        util = state.utilisation

        if util >= 0.70:

            score += 8

        elif util >= 0.60:

            score += 4

        elif util < 0.40:

            score -= 10

        # ---------------------------------------------------------------------
        # WARNINGS / ERRORS
        # ---------------------------------------------------------------------

        score -= len(state.warnings) * 1.5

        score -= len(state.errors) * 8

        # ---------------------------------------------------------------------
        # LIMIT
        # ---------------------------------------------------------------------

        score = max(
            0,
            min(score, 100)
        )

        return round(score, 2)