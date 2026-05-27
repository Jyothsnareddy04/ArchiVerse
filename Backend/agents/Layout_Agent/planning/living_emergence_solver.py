# =============================================================================
# living_emergence_solver.py
# =============================================================================

from shapely.geometry import (
    box,
    MultiPolygon
)

from state import Space

# =============================================================================
# CONSTANTS
# =============================================================================

MIN_LIVING_AREA = 140.0
MAX_LIVING_RATIO = 0.24

# =============================================================================
# ENGINE
# =============================================================================



class LivingEmergenceSolver:

    def __init__(

        self,

        engine,

        state
    ):

        self.engine = engine
        self.state = state

    # =========================================================================
    # MAIN
    # =========================================================================

    def emerge_living_room(

        self,

        living_plan=None
    ):

        print("\n[LIVING EMERGENCE]")

        residual = self.engine.remaining

        if residual is None:
            return None

        if residual.is_empty:
            return None

        # ---------------------------------------------------------------------
        # CLEAN
        # ---------------------------------------------------------------------

        residual = residual.buffer(0)

        if residual.is_empty:
            return None

        # ---------------------------------------------------------------------
        # MULTI
        # ---------------------------------------------------------------------

        if isinstance(residual, MultiPolygon):

            pieces = [

                p for p in residual.geoms

                if p.area > MIN_LIVING_AREA
            ]

            if not pieces:
                return None

            residual = max(
                pieces,
                key=lambda x: x.area
            )

        # ---------------------------------------------------------------------
        # LIMIT
        # ---------------------------------------------------------------------

        buildable_area = (
            self.state.buildable_polygon.area
        )

        max_area = (
            buildable_area
            *
            MAX_LIVING_RATIO
        )

        poly = residual

        # ---------------------------------------------------------------------
        # SHRINK IF HUGE
        # ---------------------------------------------------------------------

        while poly.area > max_area:

            poly = poly.buffer(-0.3)

            if poly.is_empty:
                return None

        poly = poly.buffer(0)

        if poly.area < MIN_LIVING_AREA:
            return None

        # ---------------------------------------------------------------------
        # ROOM NAME
        # ---------------------------------------------------------------------

        room_name = "living"

        if living_plan is not None:

            room_name = living_plan.get(
                "name",
                "living"
            )

        # ---------------------------------------------------------------------
        # COMMIT
        # ---------------------------------------------------------------------

        living = Space(

            name=room_name,

            room_type="living",

            polygon=poly,

            zone="social"
        )

        self.state.spaces.append(
            living
        )

        self.engine.subtract(
            room_name,
            poly
        )

        print(
            f"  ✔ Living : "
            f"{poly.area:.1f} sqft"
        )

        return living