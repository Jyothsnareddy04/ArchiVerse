# =============================================================================
# SEQUENTIAL SOLVER v6 — Production Multi-Variant Topology Solver
# =============================================================================
# Handles:
#
# - topology retries
# - intelligent scaling
# - variant generation
# - anchor preservation
# - circulation-aware retries
# - environmental retries
# - quality-based best selection
# =============================================================================

from copy import deepcopy

from typing import (
    List,
    Dict,
    Any
)

from state import (
    LayoutState
)

from planning.topology_solver import (
    TopologySolver
)

from validation.scoring_engine import (
    ScoringEngine
)

# =============================================================================
# CONSTANTS
# =============================================================================

ANCHOR_TYPES = {

    "parking",

    "staircase",

    "backyard",

    "lawn",

    "main_gate",

    "green_strip"
}

# =============================================================================
# ENGINE
# =============================================================================


class SequentialSolver:

    def __init__(self):

        self.scorer = ScoringEngine()

# =============================================================================
# MAIN
# =============================================================================


    def solve(

        self,

        state: LayoutState,

        room_plan: List[Dict[str, Any]],

        max_attempts: int = 4
    ) -> bool:

        print("\n" + "=" * 60)

        print("SEQUENTIAL SOLVER")

        print("=" * 60)

        variants = []

        # =========================================================================
        # ATTEMPTS
        # =========================================================================

        for attempt in range(max_attempts):

            print(

                f"\n[ATTEMPT {attempt+1}]"
            )

            # =====================================================================
            # CLONE STATE
            # =====================================================================

            working_state = deepcopy(
                state
            )

            # =====================================================================
            # SCALE
            # =====================================================================

            scale = self._attempt_scale(
                attempt
            )

            # =====================================================================
            # RESET
            # =====================================================================

            anchors = [

                s for s in working_state.spaces

                if s.room_type in ANCHOR_TYPES
            ]

            working_state.spaces = anchors

            working_state.errors = []

            working_state.warnings = []

            # =====================================================================
            # PLAN
            # =====================================================================

            scaled_plan = self._scaled_plan(

                room_plan,

                scale,

                attempt
            )

            # =====================================================================
            # TOPOLOGY
            # =====================================================================

            topology = TopologySolver()

            topology.solve_topology(

                working_state,

                scaled_plan
            )

            # =====================================================================
            # VALIDATE
            # =====================================================================

            success = self._validate_solution(
                working_state
            )

            # =====================================================================
            # SCORE
            # =====================================================================

            score = self.scorer.score(
                working_state
            )

            working_state.score = score

            variants.append(
                working_state
            )

            print(

                f"  ✔ Score:"
                f" {score:.1f}"
            )

            if success and score >= 75:

                print(
                    "  ✔ Excellent solution"
                )

                break

        # =========================================================================
        # BEST VARIANT
        # =========================================================================

        if len(variants) == 0:

            state.log(
                "Solver failed"
            )

            return False

        best = max(

            variants,

            key=lambda s: s.score
        )

        # =========================================================================
        # COPY BEST
        # =========================================================================

        state.spaces = best.spaces

        state.errors = best.errors

        state.warnings = best.warnings

        state.score = best.score

        state.remaining_polygon = (

            best.remaining_polygon
        )

        print("\n" + "=" * 60)

        print(

            f"BEST SCORE:"
            f" {best.score:.1f}"
        )

        print("=" * 60)

        return True

# =============================================================================
# SCALE
# =============================================================================


    def _attempt_scale(

        self,

        attempt
    ):

        scales = [

            1.00,

            0.94,

            0.88,

            0.82
        ]

        return scales[
            min(
                attempt,
                len(scales) - 1
            )
        ]

# =============================================================================
# PLAN
# =============================================================================


    def _scaled_plan(

        self,

        room_plan,

        scale,

        attempt
    ):

        scaled = []

        for room in room_plan:

            r = room.copy()

            # =============================================================
            # keep environmental rooms fixed
            # =============================================================

            if r["type"] in [

                "wash_area",

                "store",

                "bathroom"
            ]:

                local_scale = max(
                    0.90,
                    scale
                )

            else:

                local_scale = scale

            # =============================================================
            # progressive retry logic
            # =============================================================

            if attempt >= 2:

                if r["type"] == "living":

                    local_scale *= 0.92

                if r["type"] == "dining":

                    local_scale *= 0.90

            r["width"] *= local_scale

            r["height"] *= local_scale

            scaled.append(r)

        return scaled

# =============================================================================
# VALIDATION
# =============================================================================


    def _validate_solution(

        self,

        state
    ):

        room_types = {

            s.room_type

            for s in state.spaces
        }

        room_names = {

            s.name

            for s in state.spaces
        }

        # =========================================================================
        # CORE
        # =========================================================================

        has_living = (

            "living"

            in room_types
        )

        has_kitchen = (

            "kitchen"

            in room_types
        )

        has_master = (

            "master_bedroom"

            in room_names
        )

        # =========================================================================
        # BEDROOMS
        # =========================================================================

        bed_count = sum(

            1 for s in state.spaces

            if s.room_type in [

                "master_bedroom",

                "bedroom"
            ]
        )

        # =========================================================================
        # BATHROOMS
        # =========================================================================

        bath_count = sum(

            1 for s in state.spaces

            if s.room_type == "bathroom"
        )

        # =========================================================================
        # CORRIDORS
        # =========================================================================

        corridor_count = sum(

            1 for s in state.spaces

            if s.room_type == "corridor"
        )

        # =========================================================================
        # ENVIRONMENT
        # =========================================================================

        has_environment = any(

            s.zone == "environmental"

            for s in state.spaces
        )

        # =========================================================================
        # FINAL
        # =========================================================================

        if not has_living:

            return False

        if not has_kitchen:

            return False

        if not has_master:

            return False

        if bed_count < max(

            1,

            state.bedrooms - 1
        ):

            return False

        if bath_count < 1:

            return False

        if not has_environment:

            return False

        return True