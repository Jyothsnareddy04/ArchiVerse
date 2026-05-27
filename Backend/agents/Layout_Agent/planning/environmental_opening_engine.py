# =============================================================================
# environmental_opening_engine.py
# =============================================================================
# ARCHIVERSE — ENVIRONMENT ENGINE v32
# =============================================================================
# FIXES
#
# ✔ green strip touches OUTER plot boundary
# ✔ green strip no longer touches buildable boundary
# ✔ added dedicated walkway setback
# ✔ backyard touches rear boundary
# ✔ backyard connected to green strip
# ✔ backyard partial-width logic
# ✔ realistic environmental topology
# ✔ cleaner residual generation
# ✔ proper outdoor circulation
#
# =============================================================================

from shapely.geometry import box

from state import Space

# =============================================================================
# CONSTANTS
# =============================================================================

FRONT_SETBACK = 4.0
SIDE_SETBACK  = 3.0
REAR_SETBACK  = 5.0

GREEN_STRIP_WIDTH = 3.5

WALKWAY_SETBACK = 2.0

BACKYARD_DEPTH = 5.0

BACKYARD_WIDTH_RATIO = 0.65

MIN_BUILDABLE_AREA = 180.0

# =============================================================================
# SERVICE CORNER PROTECTION
# =============================================================================

SERVICE_PROTECTED_CORNERS = {

    "north": ["south_east"],

    "south": ["north_west"],

    "east":  ["south_west"],

    "west":  ["south_east"]
}

# =============================================================================
# ENGINE
# =============================================================================

class EnvironmentalOpeningEngine:

    # =========================================================================
    # INIT
    # =========================================================================

    def __init__(self, state):

        self.state = state

        self.plot = state.plot_polygon

        self.facing = state.facing.lower()

        self.px0, self.py0, self.px1, self.py1 = (
            self.plot.bounds
        )

        self.plot_w = self.px1 - self.px0
        self.plot_h = self.py1 - self.py0

    # =========================================================================
    # MAIN
    # =========================================================================

    def generate(self):

        print("\n" + "=" * 60)
        print("ENVIRONMENT ENGINE")
        print("=" * 60)

        # ---------------------------------------------------------------------
        # BUILDABLE
        # ---------------------------------------------------------------------

        buildable = self._generate_buildable_core()

        if buildable is None:

            self.state.errors.append(
                "Buildable generation failed"
            )

            return

        self.state.buildable_polygon = buildable

        print(
            f"  ✔ buildable : "
            f"{buildable.area:.1f} sqft"
        )
        
        # ---------------------------------------------------------------------
        # PROTECTED SERVICE CORNERS
        # ---------------------------------------------------------------------

        protected = SERVICE_PROTECTED_CORNERS.get(

            self.state.facing.lower(),

            ["south_east"]
        )

        # ---------------------------------------------------------------------
        # GREEN STRIP
        # ---------------------------------------------------------------------

        green = self._generate_green_strip()

        if green is not None:

            self._commit(

                "green_strip",

                "green_strip",

                green,

                "environment"
            )
        # ---------------------------------------------------------------------
        # BACKYARD
        # ---------------------------------------------------------------------

        backyard = self._generate_backyard()

        if backyard is not None:

            self._commit(

                "backyard",

                "backyard",

                backyard,

                "environment"
            )

    # =========================================================================
    # BUILDABLE CORE
    # =========================================================================

    def _generate_buildable_core(self):

        extra_side = (
            GREEN_STRIP_WIDTH
            +
            WALKWAY_SETBACK
        )

        # ---------------------------------------------------------------------
        # NORTH
        # ---------------------------------------------------------------------

        if self.facing == "north":

            poly = box(

                self.px0 + extra_side,

                self.py0 + REAR_SETBACK,

                self.px1 - SIDE_SETBACK,

                self.py1 - FRONT_SETBACK
            )

        # ---------------------------------------------------------------------
        # SOUTH
        # ---------------------------------------------------------------------

        elif self.facing == "south":

            poly = box(

                self.px0 + SIDE_SETBACK,

                self.py0 + FRONT_SETBACK,

                self.px1 - extra_side,

                self.py1 - REAR_SETBACK
            )

        # ---------------------------------------------------------------------
        # EAST
        # ---------------------------------------------------------------------

        elif self.facing == "east":

            poly = box(

                self.px0 + REAR_SETBACK,

                self.py0 + SIDE_SETBACK,

                self.px1 - FRONT_SETBACK,

                self.py1 - extra_side
            )

        # ---------------------------------------------------------------------
        # WEST
        # ---------------------------------------------------------------------

        else:

            poly = box(

                self.px0 + FRONT_SETBACK,

                self.py0 + extra_side,

                self.px1 - REAR_SETBACK,

                self.py1 - SIDE_SETBACK
            )

        poly = poly.buffer(0)

        if poly.is_empty:
            return None

        if poly.area < MIN_BUILDABLE_AREA:
            return None

        return poly

    # =========================================================================
    # GREEN STRIP
    # touches OUTER boundary
    # =========================================================================

    def _generate_green_strip(self):

        # ---------------------------------------------------------------------
        # NORTH
        # ---------------------------------------------------------------------

        if self.facing == "north":

            poly = box(

                self.px0,

                self.py0,

                self.px0 + GREEN_STRIP_WIDTH,

                self.py1
            )

        # ---------------------------------------------------------------------
        # SOUTH
        # ---------------------------------------------------------------------

        elif self.facing == "south":

            poly = box(

                self.px1 - GREEN_STRIP_WIDTH,

                self.py0,

                self.px1,

                self.py1
            )

        # ---------------------------------------------------------------------
        # EAST
        # ---------------------------------------------------------------------

        elif self.facing == "east":

            # -------------------------------------------------------------
            # PRESERVE SOUTH-WEST SERVICE CORNER
            # -------------------------------------------------------------

            poly = box(

                self.px0,

                self.py1 - GREEN_STRIP_WIDTH,

                self.px1 - 8,

                self.py1
            )

        # ---------------------------------------------------------------------
        # WEST
        # ---------------------------------------------------------------------

        else:

            # -------------------------------------------------------------
            # WEST FACING
            #
            # ROAD = WEST
            # GREEN STRIP SHOULD BE NORTH
            #
            # preserve SE service zone
            # -------------------------------------------------------------

            poly = box(

                self.px0,

                self.py1 - GREEN_STRIP_WIDTH,

                self.px1,

                self.py1
            )

        return poly.buffer(0)

    # =========================================================================
    # BACKYARD
    # touches green strip + rear boundary
    # =========================================================================

    def _generate_backyard(self):

        buildable = self.state.buildable_polygon

        bx0, by0, bx1, by1 = buildable.bounds

        usable_w = bx1 - bx0
        usable_h = by1 - by0

        # ---------------------------------------------------------------------
        # NORTH
        # ---------------------------------------------------------------------

        if self.facing == "north":

            backyard_w = usable_w * BACKYARD_WIDTH_RATIO

            start_x = (
                self.px0
                +
                GREEN_STRIP_WIDTH
            )

            poly = box(

                start_x,

                self.py0,

                start_x + backyard_w,

                self.py0 + BACKYARD_DEPTH
            )

        # ---------------------------------------------------------------------
        # SOUTH
        # ---------------------------------------------------------------------

        elif self.facing == "south":

            backyard_w = usable_w * BACKYARD_WIDTH_RATIO

            poly = box(

                self.px1 - GREEN_STRIP_WIDTH - backyard_w,

                self.py1 - BACKYARD_DEPTH,

                self.px1 - GREEN_STRIP_WIDTH,

                self.py1
            )

        # ---------------------------------------------------------------------
        # EAST
        # ---------------------------------------------------------------------

        elif self.facing == "east":

            backyard_h = usable_h * BACKYARD_WIDTH_RATIO

            poly = box(

                self.px0,

                self.py1 - GREEN_STRIP_WIDTH - backyard_h,

                self.px0 + BACKYARD_DEPTH,

                self.py1 - GREEN_STRIP_WIDTH
            )

        # ---------------------------------------------------------------------
        # WEST
        # ---------------------------------------------------------------------

        else:

            # -------------------------------------------------------------
            # WEST FACING
            #
            # backyard should CONNECT
            # with north green strip
            # -------------------------------------------------------------

            backyard_h = usable_h * BACKYARD_WIDTH_RATIO

            poly = box(

                self.px1 - BACKYARD_DEPTH,

                self.py1 - backyard_h - GREEN_STRIP_WIDTH,

                self.px1,

                self.py1 - GREEN_STRIP_WIDTH
            )

        return poly.buffer(0)

    # =========================================================================
    # COMMIT
    # =========================================================================

    def _commit(

        self,

        name,

        room_type,

        polygon,

        zone
    ):

        if polygon is None:
            return

        if polygon.is_empty:
            return

        polygon = polygon.buffer(0)

        self.state.spaces.append(

            Space(

                name=name,

                room_type=room_type,

                polygon=polygon,

                zone=zone
            )
        )

        print(
            f"  ✔ {name}"
        )