# =============================================================================
# CIRCULATION ENGINE v11
# =============================================================================
# Connectivity Validation Engine
#
# RESPONSIBILITIES
#
# - validate room reachability
# - validate circulation connectivity
# - identify isolated rooms
# - validate living accessibility
#
# DOES NOT:
#
# - create corridors
# - create geometry
# - repair topology
# =============================================================================

from shapely.geometry import (
    MultiPolygon
)

from state import (
    LayoutState
)

# =============================================================================
# ENGINE
# =============================================================================

class CirculationEngine:

    def __init__(

        self,

        engine,

        state: LayoutState
    ):

        self.engine = engine

        self.state = state
        
    # =========================================================================
    # CONNECTIVITY VALIDATION ONLY
    # =========================================================================

    def repair_connectivity(self):

        print("\n[CIRCULATION CHECK]")

        disconnected = []

        living = self.state.get_space(
            "living"
        )

        if living is None:

            return []

        for s in self.state.spaces:

            if s.name == living.name:
                continue

            # =========================================================
            # IGNORE ENVIRONMENT
            # =========================================================

            if s.zone == "environmental":
                continue

            # =========================================================
            # CONNECTIVITY
            # =========================================================

            connected = self._is_connected(
                s,
                living
            )

            if not connected:

                disconnected.append(
                    s.name
                )

        if disconnected:

            print(
                f"  ⚠ Disconnected: {disconnected}"
            )

        else:

            print(
                "  ✔ Connectivity valid"
            )

        return disconnected

    # =========================================================================
    # CONNECTED
    # =========================================================================

    def _is_connected(self, a, b):

        # =============================================================
        # SHARED WALL
        # =============================================================

        shared = a.polygon.buffer(0.3).boundary.intersection(

            b.polygon.buffer(0.3).boundary
        )

        if shared.length > 1:

            return True

        # =============================================================
        # BUFFERED TOPOLOGY
        # =============================================================

        overlap = a.polygon.buffer(1).intersection(

            b.polygon.buffer(1)
        )

        if overlap.area > 2:

            return True

        return False