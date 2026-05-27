# =============================================================================
# SCORING ENGINE v5
# =============================================================================
# Production topology scoring engine
#
# Scores:
#
# - topology quality
# - circulation
# - zoning
# - environmental logic
# - compactness
# - adjacency
# - setbacks
# - utilisation
# - architectural intelligence
# =============================================================================

from state import LayoutState
import os
import sys

UTILS_DIR = os.path.abspath(

    os.path.join(

        os.path.dirname(__file__),

        "../utils"
    )
)

if UTILS_DIR not in sys.path:

    sys.path.insert(
        0,
        UTILS_DIR
    )
    
    
from utils.geometry_utils import (

    are_adjacent,

    aspect_ratio,

    compactness,

    polygon_quality_score,

    touches_exterior
)

# =============================================================================
# ENGINE
# =============================================================================


class ScoringEngine:

    def score(

        self,

        state: LayoutState
    ):

        print("\n" + "=" * 60)

        print("TOPOLOGY SCORING ENGINE")

        print("=" * 60)

        total = 0

        # =========================================================================
        # UTILISATION
        # =========================================================================

        total += self._score_utilisation(
            state
        )

        # =========================================================================
        # OVERLAPS
        # =========================================================================

        total += self._score_geometry(
            state
        )

        # =========================================================================
        # ROOM QUALITY
        # =========================================================================

        total += self._score_room_quality(
            state
        )

        # =========================================================================
        # ADJACENCY
        # =========================================================================

        total += self._score_adjacency(
            state
        )

        # =========================================================================
        # ZONING
        # =========================================================================

        total += self._score_zoning(
            state
        )

        # =========================================================================
        # CIRCULATION
        # =========================================================================

        total += self._score_circulation(
            state
        )

        # =========================================================================
        # ENVIRONMENTAL
        # =========================================================================

        total += self._score_environment(
            state
        )

        # =========================================================================
        # VASTU
        # =========================================================================

        total += self._score_vastu(
            state
        )

        # =========================================================================
        # PENALTIES
        # =========================================================================

        total -= self._penalties(
            state
        )

        total = max(
            0,
            min(total, 100)
        )

        state.score = round(total, 1)

        print("\n" + "=" * 60)

        print(

            f"FINAL SCORE:"
            f" {state.score}/100"
        )

        print("=" * 60)

        return state.score

# =============================================================================
# UTILISATION
# =============================================================================


    def _score_utilisation(

        self,

        state
    ):

        util = state.utilisation

        score = 0

        if util >= 0.85:

            score = 20

        elif util >= 0.75:

            score = 17

        elif util >= 0.65:

            score = 14

        elif util >= 0.55:

            score = 10

        else:

            score = 5

        print(

            f"  Utilisation:"
            f" {score}/20"
        )

        return score

# =============================================================================
# GEOMETRY
# =============================================================================


    def _score_geometry(

        self,

        state
    ):

        errors = [

            e for e in state.errors

            if "overlap" in e.lower()
        ]

        score = max(

            0,

            15 - (len(errors) * 5)
        )

        print(

            f"  Geometry:"
            f" {score}/15"
        )

        return score

# =============================================================================
# ROOM QUALITY
# =============================================================================


    def _score_room_quality(

        self,

        state
    ):

        total = 0

        count = 0

        for s in state.spaces:

            quality = polygon_quality_score(
                s.polygon
            )

            total += quality

            count += 1

        if count == 0:

            return 0

        avg = total / count

        score = (

            avg / 100
        ) * 15

        print(

            f"  Room Quality:"
            f" {score:.1f}/15"
        )

        return score

# =============================================================================
# ADJACENCY
# =============================================================================


    def _score_adjacency(

        self,

        state
    ):

        score = 15

        rules = [

            (
                "kitchen",
                "wash_area"
            ),

            (
                "kitchen",
                "dining"
            )
        ]

        for a_name, b_name in rules:

            a = state.get_space(a_name)

            b = state.get_space(b_name)

            if a is None or b is None:

                continue

            if not are_adjacent(

                a.polygon,

                b.polygon,

                tolerance=2
            ):

                score -= 3

        score = max(score, 0)

        print(

            f"  Adjacency:"
            f" {score}/15"
        )

        return score

# =============================================================================
# ZONING
# =============================================================================


    def _score_zoning(

        self,

        state
    ):

        score = 10

        private_rooms = [

            s for s in state.spaces

            if s.zone == "private"
        ]

        social_rooms = [

            s for s in state.spaces

            if s.zone == "social"
        ]

        for p in private_rooms:

            for s in social_rooms:

                if are_adjacent(

                    p.polygon,

                    s.polygon,

                    tolerance=2
                ):

                    score -= 0.5

        score = max(score, 0)

        print(

            f"  Zoning:"
            f" {score}/10"
        )

        return score

# =============================================================================
# ENVIRONMENT
# =============================================================================


    def _score_environment(

        self,

        state
    ):

        score = 10

        if state.buildable_polygon is None:

            return 0

        required = [

            "living",

            "kitchen",

            "wash_area",

            "bathroom"
        ]

        for s in state.spaces:

            if s.room_type not in required:

                continue

            ext = touches_exterior(

                s.polygon,

                state.buildable_polygon,

                min_touch=2
            )

            if not ext:

                score -= 2

        backyard = state.get_space(
            "backyard"
        )

        if backyard is None:

            score -= 2

        score = max(score, 0)

        print(

            f"  Environmental:"
            f" {score}/10"
        )

        return score

# =============================================================================
# VASTU
# =============================================================================


    def _score_vastu(

        self,

        state
    ):

        warnings = [

            w for w in state.warnings

            if "vastu" in w.lower()
        ]

        score = max(

            0,

            5 - len(warnings)
        )

        print(

            f"  Vastu:"
            f" {score}/5"
        )

        return score

# =============================================================================
# PENALTIES
# =============================================================================


    def _penalties(

        self,

        state
    ):

        penalty = 0

        # =========================================================================
        # ERRORS
        # =========================================================================

        penalty += len(state.errors) * 3

        # =========================================================================
        # EXTREME RATIOS
        # =========================================================================

        for s in state.spaces:

            ratio = aspect_ratio(
                s.polygon
            )

            if ratio > 6:

                penalty += 2

        # =========================================================================
        # LOW COMPACTNESS
        # =========================================================================

        for s in state.spaces:

            comp = compactness(
                s.polygon
            )

            if comp < 0.12:

                penalty += 2

        print(

            f"  Penalties:"
            f" -{penalty}"
        )

        return penalty