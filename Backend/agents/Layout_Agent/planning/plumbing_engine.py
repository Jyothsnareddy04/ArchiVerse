# =============================================================================
# PLUMBING ENGINE v7
# =============================================================================
# INTERNAL BATHROOM TOPOLOGY ENGINE
# =============================================================================

from shapely.geometry import (
    box
)

from state import LayoutState


# =============================================================================
# ENGINE
# =============================================================================

class PlumbingEngine:

    def __init__(

        self,

        engine,

        state: LayoutState
    ):

        self.engine = engine

        self.state = state

        self.facing = state.facing.lower()

        self.bx0, self.by0, self.bx1, self.by1 = (

            state.buildable_polygon.bounds
        )

    # =========================================================================
    # ATTACHED BATHROOM
    # =========================================================================

    def _place_attached_bath(

        self,

        bedroom_space
    ):

        if bedroom_space is None:
            return None

        # =====================================================
        # STANDARD SIZE
        # =====================================================

        bath_w = 5
        bath_h = 7

        # =====================================================
        # FACING SPECIFIC CORNER
        # =====================================================

        if self.facing == "north":

            preferred = "south-west"

        elif self.facing == "east":

            preferred = "south-west"

        elif self.facing == "south":

            preferred = "north-east"

        else:

            preferred = "south-west"

        # =====================================================
        # INTERNAL BATH
        # =====================================================

        bath_poly = self._internal_bathroom(

            bedroom_space.polygon,

            bath_w,

            bath_h,

            preferred
        )

        if bath_poly is None:
            return None

        # =====================================================
        # CREATE SPACE
        # =====================================================

        bathroom_space = self.add_room(

            "bathroom",

            bath_poly
        )

        return bathroom_space

    # =========================================================================
    # INTERNAL CARVE
    # =========================================================================

    def _internal_bathroom(

        self,

        bedroom_poly,

        bath_w,

        bath_h,

        preferred_edge
    ):

        bx0, by0, bx1, by1 = (

            bedroom_poly.bounds
        )

        # =====================================================
        # SOUTH WEST
        # =====================================================

        if preferred_edge == "south-west":

            bath = box(

                bx0,
                by0,

                bx0 + bath_w,
                by0 + bath_h
            )

        # =====================================================
        # SOUTH EAST
        # =====================================================

        elif preferred_edge == "south-east":

            bath = box(

                bx1 - bath_w,
                by0,

                bx1,
                by0 + bath_h
            )

        # =====================================================
        # NORTH WEST
        # =====================================================

        elif preferred_edge == "north-west":

            bath = box(

                bx0,
                by1 - bath_h,

                bx0 + bath_w,
                by1
            )

        # =====================================================
        # NORTH EAST
        # =====================================================

        else:

            bath = box(

                bx1 - bath_w,
                by1 - bath_h,

                bx1,
                by1
            )

        # =====================================================
        # MUST STAY INSIDE
        # =====================================================

        if not bath.within(
            bedroom_poly
        ):

            return None

        # =====================================================
        # MUST TOUCH EXTERIOR
        # =====================================================

        if not self._touches_exterior(
            bath
        ):

            return None

        # =====================================================
        # COLLISION SAFE
        # =====================================================

        if self._collides(
            bath
        ):

            return None

        return bath.buffer(0)

    # =========================================================================
    # COMMON BATHROOM
    # =========================================================================

    def place_common_bathroom(

        self,

        plan
    ):

        print("\n[COMMON BATHROOM]")

        width = plan["width"]
        height = plan["height"]

        candidates = [

            # SW
            box(
                self.bx0,
                self.by0,
                self.bx0 + width,
                self.by0 + height
            ),

            # SE
            box(
                self.bx1 - width,
                self.by0,
                self.bx1,
                self.by0 + height
            ),

            # NW
            box(
                self.bx0,
                self.by1 - height,
                self.bx0 + width,
                self.by1
            ),

            # NE
            box(
                self.bx1 - width,
                self.by1 - height,
                self.bx1,
                self.by1
            )
        ]

        for candidate in candidates:

            if not candidate.within(
                self.state.buildable_polygon
            ):
                continue

            if self._collides(candidate):
                continue

            if not self._touches_exterior(
                candidate
            ):
                continue

            print(
                "  ✔ Common bathroom anchored"
            )

            return candidate.buffer(0)

        return None

    # =========================================================================
    # STACK WET ZONES
    # =========================================================================

    def stack_wet_zones(

        self
    ):

        return

    # =========================================================================
    # PLACE INTERNAL BATHROOM
    # =========================================================================

    def place_internal_bathroom(

        self,

        bedroom_poly,

        bath_plan
    ):

        bw = bath_plan["width"]
        bh = bath_plan["height"]

        bx0, by0, bx1, by1 = (

            bedroom_poly.bounds
        )

        corners = [

            box(
                bx0,
                by0,
                bx0 + bw,
                by0 + bh
            ),

            box(
                bx1 - bw,
                by0,
                bx1,
                by0 + bh
            ),

            box(
                bx0,
                by1 - bh,
                bx0 + bw,
                by1
            ),

            box(
                bx1 - bw,
                by1 - bh,
                bx1,
                by1
            )
        ]

        for bath in corners:

            if not bath.within(
                bedroom_poly
            ):
                continue

            if not self._touches_exterior(
                bath
            ):
                continue

            if self._collides(
                bath
            ):
                continue

            return (

                bedroom_poly,

                bath.buffer(0)
            )

        return (

            bedroom_poly,

            None
        )

    # =========================================================================
    # EXTERIOR TOUCH
    # =========================================================================

    def _touches_exterior(

        self,

        poly
    ):

        minx, miny, maxx, maxy = (
            poly.bounds
        )

        return (

            abs(minx - self.bx0) < 0.6
            or
            abs(maxx - self.bx1) < 0.6
            or
            abs(miny - self.by0) < 0.6
            or
            abs(maxy - self.by1) < 0.6
        )

    # =========================================================================
    # COLLISION
    # =========================================================================

    def _collides(

        self,

        poly
    ):

        IGNORE_TYPES = {

            "bedroom",
            "master_bedroom",
            "bathroom"
        }

        for s in self.state.spaces:

            # =====================================================
            # IGNORE BEDROOM COLLISION
            # =====================================================

            if s.room_type in IGNORE_TYPES:
                continue

            inter = poly.intersection(
                s.polygon
            )

            if inter.is_empty:
                continue

            if inter.area > 4:

                return True

        return False

    # =========================================================================
    # ADD ROOM
    # =========================================================================

    def add_room(

        self,

        room_type,

        polygon
    ):

        from state import Space

        zone = "private"

        space = Space(

            name=room_type,

            room_type=room_type,

            polygon=polygon,

            zone=zone
        )

        self.state.spaces.append(
            space
        )

        return space