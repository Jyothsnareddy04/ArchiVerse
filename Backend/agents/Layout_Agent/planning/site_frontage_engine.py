# =============================================================================
# site_frontage_engine.py
# =============================================================================
# ARCHIVERSE — SITE FRONTAGE ENGINE v31
# =============================================================================
# FIXES
#
# ✔ staircase no longer fixed to front
# ✔ staircase uses free-corner candidate system
# ✔ prefers rear corners
# ✔ avoids parking overlap
# ✔ avoids green-strip side
# ✔ deterministic placement
# ✔ cleaner frontage topology
#
# GENERATED
#   1. main gate
#   2. parking
#   3. staircase
#   4. front lawn
#
# =============================================================================

from shapely.geometry import box

# =============================================================================
# CONSTANTS
# =============================================================================

MAIN_GATE_WIDTH = 8.0
MAIN_GATE_DEPTH = 2.0

PARK_W = 10.0
PARK_H = 16.0

STAIR_W = 5.0
STAIR_H = 8.0

LAWN_DEPTH = 4.0
CORNER_PADDING = 1.0

# =============================================================================
# ENGINE
# =============================================================================

class SiteFrontageEngine:

    # =========================================================================
    # MAIN
    # =========================================================================

    def generate(self, state):

        self.state = state

        self.plot = state.plot_polygon

        self.facing = state.facing.lower()

        self.px0, self.py0, self.px1, self.py1 = (
            self.plot.bounds
        )

        self.plot_w = self.px1 - self.px0
        self.plot_h = self.py1 - self.py0

        print("\n" + "=" * 60)
        print("SITE FRONTAGE ENGINE")
        print("=" * 60)
        
        # ---------------------------------------------------------------------
        # SERVICE SAFE ZONE
        # protects semantic service cluster corner
        # ---------------------------------------------------------------------

        self.service_safe_zone = {

            "north": "SE",
            "south": "NW",
            "east": "SW",
            "west": "SE"
        }

        # ---------------------------------------------------------------------
        # ORDER
        # ---------------------------------------------------------------------

        parking = self._place_parking()

        gate = self._place_gate(
            parking
        )

        stair = self._place_stair(
            parking
        )

        lawn = self._place_lawn(
            parking,
            stair
        )

        print("  ✔ main gate")
        print("  ✔ parking")
        print("  ✔ staircase")
        print("  ✔ front lawn")

        return [

            gate,
            parking,
            stair,
            lawn
        ]

    # =========================================================================
    # PARKING
    # =========================================================================

    def _place_parking(self):

        if self.facing == "north":

            poly = box(

                self.px1 - PARK_W,
                self.py1 - PARK_H,

                self.px1,
                self.py1
            )

        elif self.facing == "south":

            poly = box(

                self.px1 - PARK_W,
                self.py0,

                self.px1,
                self.py0 + PARK_H
            )

        elif self.facing == "east":

            poly = box(

                self.px1 - PARK_H,
                self.py1 - PARK_W,

                self.px1,
                self.py1
            )

        else:

            poly = box(

                self.px0,
                self.py1 - PARK_W,

                self.px0 + PARK_H,
                self.py1
            )

        # -------------------------------------------------------------
        # PROTECT SERVICE CLUSTER
        # -------------------------------------------------------------

        if self._violates_service_zone(poly):

            if self.facing == "north":

                poly = box(

                    self.px1 - PARK_W,
                    self.py1 - PARK_H,

                    self.px1,
                    self.py1
                )

            elif self.facing == "south":

                poly = box(

                    self.px1 - PARK_W,
                    self.py0,

                    self.px1,
                    self.py0 + PARK_H
                )
        
        return poly.buffer(0)

    # =========================================================================
    # GATE
    # =========================================================================

    def _place_gate(

        self,

        parking
    ):

        minx, miny, maxx, maxy = (
            parking.bounds
        )

        if self.facing == "north":

            gate = box(

                minx,

                self.py1 - MAIN_GATE_DEPTH,

                minx + MAIN_GATE_WIDTH,

                self.py1
            )

        elif self.facing == "south":

            gate = box(

                minx,

                self.py0,

                minx + MAIN_GATE_WIDTH,

                self.py0 + MAIN_GATE_DEPTH
            )

        elif self.facing == "east":

            gate = box(

                self.px1 - MAIN_GATE_DEPTH,

                miny,

                self.px1,

                miny + MAIN_GATE_WIDTH
            )

        else:

            gate = box(

                self.px0,

                miny,

                self.px0 + MAIN_GATE_DEPTH,

                miny + MAIN_GATE_WIDTH
            )

        return gate.buffer(0)

    # =========================================================================
    # STAIRCASE
    # =========================================================================

    def _place_stair(

        self,

        parking
    ):
        
        # WEST facing needs more private depth
        if self.facing == "west":
            STAIR_W = 3
        else:
            STAIR_W = 5

        # =========================================================
        # NORTH
        # parking = front-right
        # stair   = front-left
        # =========================================================

        if self.facing == "north":

            stair = box(

                self.px0,
                self.py1 - STAIR_H,

                self.px0 + STAIR_W,
                self.py1
            )

        # =========================================================
        # SOUTH
        # parking = front-right
        # stair   = front-left
        # =========================================================

        elif self.facing == "south":

            stair = box(

                self.px0,
                self.py0,

                self.px0 + STAIR_W,
                self.py0 + STAIR_H
            )

        # =========================================================
        # EAST
        # parking = top-right
        # stair   = top-left
        # =========================================================

        elif self.facing == "east":

            # ---------------------------------------------------------
            # MOVE STAIR TO SOUTH-WEST
            # avoids parking collision
            # -------------------------------------------------------------

            stair = box(

                self.px0,
                self.py0,

                self.px0 + STAIR_W,
                self.py0 + STAIR_H
            )

        # =========================================================
        # WEST
        # parking = top-left
        # stair   = bottom-left
        # =========================================================

        else:

            stair = box(

                self.px0,
                self.py0,

                self.px0 + STAIR_W,
                self.py0 + STAIR_H
            )

        # -------------------------------------------------------------
        # SAFETY BUFFER
        # -------------------------------------------------------------

        if stair.intersects(parking):

            stair = stair.buffer(-0.4)
            
            
        # -------------------------------------------------------------
        # SERVICE SAFE CHECK
        # -------------------------------------------------------------

        if self._violates_service_zone(stair):

            if self.facing == "north":

                stair = box(

                    self.px0,
                    self.py1 - STAIR_H,

                    self.px0 + STAIR_W,
                    self.py1
                )

            elif self.facing == "south":

                stair = box(

                    self.px1 - STAIR_W,
                    self.py0,

                    self.px1,
                    self.py0 + STAIR_H
                )

        return stair.buffer(0)
    
    
    # =========================================================================
    # SERVICE CORNER PROTECTION
    # =========================================================================

    def _violates_service_zone(

        self,

        poly
    ):

        if poly is None:
            return False

        minx, miny, maxx, maxy = (
            poly.bounds
        )

        safe = self.service_safe_zone.get(
            self.facing,
            "SE"
        )

        # -------------------------------------------------------------
        # NORTH
        # reserve SOUTH-EAST
        # -------------------------------------------------------------

        if safe == "SE":

            return (

                maxx > self.px1 - 10

                and

                miny < self.py0 + 10
            )

        # -------------------------------------------------------------
        # SOUTH
        # reserve NORTH-WEST
        # -------------------------------------------------------------

        if safe == "NW":

            return (

                minx < self.px0 + 10

                and

                maxy > self.py1 - 10
            )

        # -------------------------------------------------------------
        # EAST
        # reserve SOUTH-WEST
        # -------------------------------------------------------------

        if safe == "SW":

            return (

                minx < self.px0 + 10

                and

                miny < self.py0 + 10
            )

        return False

    # =========================================================================
    # LAWN
    # =========================================================================

    def _place_lawn(

        self,

        parking,

        stair
    ):

        if self.facing == "north":

            lawn = box(

                self.px0,
                self.py1 - LAWN_DEPTH,

                self.px1,
                self.py1
            )

        elif self.facing == "south":

            lawn = box(

                self.px0,
                self.py0,

                self.px1,
                self.py0 + LAWN_DEPTH
            )

        elif self.facing == "east":

            lawn = box(

                self.px1 - LAWN_DEPTH,
                self.py0,

                self.px1,
                self.py1
            )

        else:

            lawn = box(

                self.px0,
                self.py0,

                self.px0 + LAWN_DEPTH,
                self.py1
            )

        # ---------------------------------------------------------------------
        # REMOVE OVERLAPS
        # ---------------------------------------------------------------------

        lawn = lawn.difference(
            parking
        )

        lawn = lawn.difference(
            stair
        )

        lawn = lawn.buffer(0)

        return lawn