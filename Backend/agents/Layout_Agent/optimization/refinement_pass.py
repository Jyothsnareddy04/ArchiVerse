# =============================================================================
# refinement_pass.py
# =============================================================================

from shapely.geometry import (
    box,
    MultiPolygon
)

from shapely.ops import unary_union

# =============================================================================
# ENGINE
# =============================================================================

class RefinementPass:

    # =========================================================================
    # MAIN
    # =========================================================================

    def refine(

        self,

        state
    ):

        print("\n[REFINEMENT PASS]")

        for space in state.spaces:

            # =============================================================
            # SKIP NON-ROOMS
            # =============================================================

            if space.room_type in [

                "main_gate",

                "green_strip",

                "backyard"
            ]:
                continue

            # =============================================================
            # SAFE CLEANUP
            # =============================================================

            self._orthogonalize(
                state,
                space
            )

            self._snap_to_grid(
                state,
                space
            )

            self._remove_slivers(
                state,
                space
            )

        # =============================================================
        # SOCIAL CLEANUP
        # =============================================================

        self._straighten_living(
            state
        )

        self._improve_dining(
            state
        )

        print(
            "  ✔ Architectural refinement complete"
        )

    # =========================================================================
    # ORTHOGONAL
    # =========================================================================

    def _orthogonalize(

        self,

        state,

        space
    ):

        # =============================================================
        # KEEP EXISTING GEOMETRY
        # =============================================================

        poly = space.polygon

        if poly.is_empty:
            return

        if not poly.is_valid:
            return

        self._safe_replace(

            state,
            space,
            poly
        )

    # =========================================================================
    # GRID
    # =========================================================================

    def _snap_to_grid(

        self,

        state,

        space
    ):

        minx, miny, maxx, maxy = (

            space.polygon.bounds
        )

        step = 0.5

        minx = round(minx / step) * step
        miny = round(miny / step) * step

        maxx = round(maxx / step) * step
        maxy = round(maxy / step) * step

        candidate = box(

            minx,
            miny,

            maxx,
            maxy
        )

        self._safe_replace(

            state,
            space,
            candidate
        )

    # =========================================================================
    # SLIVERS
    # =========================================================================

    def _remove_slivers(

        self,

        state,

        space
    ):

        poly = space.polygon.buffer(
            0.08
        ).buffer(
            -0.08
        )

        if poly.is_empty:
            return

        if isinstance(
            poly,
            MultiPolygon
        ):

            poly = max(

                poly.geoms,

                key=lambda g: g.area
            )

        self._safe_replace(

            state,
            space,
            poly
        )

    # =========================================================================
    # LIVING
    # =========================================================================

    def _straighten_living(

        self,

        state
    ):

        return
    # =========================================================================
    # DINING
    # =========================================================================

    def _improve_dining(

        self,

        state
    ):

        dining = state.get_space(
            "dining"
        )

        if dining is None:
            return

        poly = dining.polygon.buffer(
            0.05
        ).buffer(
            -0.05
        )

        self._safe_replace(

            state,
            dining,
            poly
        )

    # =========================================================================
    # SAFE REPLACE
    # =========================================================================

    def _safe_replace(

        self,

        state,

        target,

        candidate
    ):

        if candidate is None:
            return

        if candidate.is_empty:
            return

        # =============================================================
        # BUILDABLE CHECK
        # =============================================================

        if not candidate.within(

            state.buildable_polygon
        ):

            return

        # =============================================================
        # COLLISION CHECK
        # =============================================================

        for other in state.spaces:

            if other == target:
                continue

            inter = candidate.intersection(
                other.polygon
            )

            if inter.area > 12:

                return

        if not candidate.is_valid:
            return
        
        target.polygon = candidate