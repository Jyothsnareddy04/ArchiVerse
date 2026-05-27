# =============================================================================
# ANCHOR ENGINE v7 — Strong Architectural Boundary Anchors
# =============================================================================

from shapely.geometry import (
    box,
    MultiPolygon
)

from shapely.ops import unary_union

from state import (
    LayoutState,
    Space
)

from config.constants import *

# =============================================================================
# ENGINE
# =============================================================================

class AnchorEngine:

    # =========================================================================
    # MAIN
    # =========================================================================

    def place_all_anchors(

        self,

        state: LayoutState
    ):

        print("\n" + "=" * 60)

        print("ANCHOR ENGINE")

        print("=" * 60)

        # =============================================================
        # PLOT + BUILDABLE FIRST
        # =============================================================

        self._reserve_environment(
            state
        )

        # =============================================================
        # MAIN GATE
        # =============================================================

        self.place_main_gate(
            state
        )

        # =============================================================
        # PARKING
        # =============================================================

        self.place_parking(
            state
        )

        # =============================================================
        # STAIRCASE
        # =============================================================

        self.place_staircase(
            state
        )

        # =============================================================
        # FRONT OPEN
        # =============================================================

        self.place_front_open_zone(
            state
        )

        # =============================================================
        # GREEN STRIPS
        # =============================================================

        self.place_side_green_strips(
            state
        )

        # =============================================================
        # BACKYARD
        # =============================================================

        self.place_backyard(
            state
        )

        # =============================================================
        # FINAL BUILDABLE
        # =============================================================

        self.finalize_buildable_polygon(
            state
        )

        print("\n✔ Anchor placement complete")

    # =========================================================================
    # ENVIRONMENT RESERVE
    # =========================================================================

    def _reserve_environment(

        self,

        state
    ):

        state.anchor_reserved = []

    # =========================================================================
    # FINAL BUILDABLE
    # =========================================================================

    def finalize_buildable_polygon(

        self,

        state
    ):

        reserved = [

            s.polygon.buffer(0.3)

            for s in state.spaces

            if s.room_type in [

                "parking",
                "staircase",
                "lawn",
                "green_strip",
                "backyard"
            ]
        ]

        if len(reserved) > 0:

            blocked = unary_union(
                reserved
            )

            buildable = (

                state.buildable_polygon.difference(
                    blocked
                )
            )

            buildable = buildable.buffer(0)

            if isinstance(
                buildable,
                MultiPolygon
            ):

                pieces = [

                    p for p in buildable.geoms
                    if p.area > 100
                ]

                if len(pieces) > 0:

                    buildable = max(
                        pieces,
                        key=lambda g: g.area
                    )

            state.buildable_polygon = buildable

        print(
            "  ✔ Buildable polygon preserved"
        )

        print(
            f"    Area: "
            f"{state.buildable_polygon.area:.1f} sqft"
        )

    # =========================================================================
    # MAIN GATE
    # =========================================================================

    def place_main_gate(

        self,

        state
    ):

        px0, py0, px1, py1 = (
            state.plot_polygon.bounds
        )

        facing = state.facing

        gate_w = MAIN_GATE_W

        margin = 2

        if facing == "north":

            poly = box(

                px1 - gate_w - margin,
                py1 - 0.5,

                px1 - margin,
                py1 + 0.5
            )

        elif facing == "south":

            poly = box(

                px1 - gate_w - margin,
                py0 - 0.5,

                px1 - margin,
                py0 + 0.5
            )

        elif facing == "east":

            poly = box(

                px1 - 0.5,
                py1 - gate_w - margin,

                px1 + 0.5,
                py1 - margin
            )

        else:

            poly = box(

                px0 - 0.5,
                py1 - gate_w - margin,

                px0 + 0.5,
                py1 - margin
            )

        self._commit(

            state,

            "main_gate",

            "main_gate",

            poly,

            "circulation"
        )

        print(
            f"  ✔ Main gate ({facing})"
        )

    # =========================================================================
    # PARKING
    # =========================================================================

    def place_parking(

        self,

        state
    ):

        px0, py0, px1, py1 = (
            state.plot_polygon.bounds
        )

        facing = state.facing

        pw = PARKING_PREF_W
        ph = PARKING_PREF_H

        front_depth = max(
            15,
            ph
        )

        if facing == "north":

            poly = box(

                px1 - pw,
                py1 - front_depth,

                px1,
                py1
            )

        elif facing == "south":

            poly = box(

                px1 - pw,
                py0,

                px1,
                py0 + front_depth
            )

        elif facing == "east":

            poly = box(

                px1 - front_depth,
                py1 - ph,

                px1,
                py1
            )

        else:

            poly = box(

                px0,
                py1 - ph,

                px0 + front_depth,
                py1
            )

        self._commit(

            state,

            "parking",

            "parking",

            poly,

            "circulation"
        )

        print(
            "  ✔ Parking attached"
        )

    # =========================================================================
    # STAIRCASE
    # =========================================================================

    def place_staircase(

        self,

        state
    ):

        px0, py0, px1, py1 = (
            state.plot_polygon.bounds
        )

        facing = state.facing

        stair_w = STAIR_TOTAL_W
        stair_h = STAIR_MIN_H

        offset = 3

        if facing == "north":

            poly = box(

                px0 + offset,
                py0 + offset,

                px0 + offset + stair_w,
                py0 + offset + stair_h
            )

        elif facing == "south":

            poly = box(

                px0 + offset,
                py1 - stair_h - offset,

                px0 + offset + stair_w,
                py1 - offset
            )

        elif facing == "east":

            poly = box(

                px0 + offset,
                py0 + offset,

                px0 + offset + stair_w,
                py0 + offset + stair_h
            )

        else:

            poly = box(

                px1 - stair_w - offset,
                py0 + offset,

                px1 - offset,
                py0 + offset + stair_h
            )

        blockers = unary_union([

            s.polygon.buffer(0.5)

            for s in state.spaces
        ])

        if poly.intersects(blockers):

            poly = poly.translate(0, 3)

        self._commit(

            state,

            "staircase",

            "staircase",

            poly,

            "circulation"
        )

        print(
            "  ✔ Staircase"
        )

    # =========================================================================
    # FRONT OPEN
    # =========================================================================

    def place_front_open_zone(

        self,

        state
    ):

        px0, py0, px1, py1 = (
            state.plot_polygon.bounds
        )

        facing = state.facing

        depth = 6

        if facing == "north":

            poly = box(
                px0,
                py1 - depth,
                px1,
                py1
            )

        elif facing == "south":

            poly = box(
                px0,
                py0,
                px1,
                py0 + depth
            )

        elif facing == "east":

            poly = box(
                px1 - depth,
                py0,
                px1,
                py1
            )

        else:

            poly = box(
                px0,
                py0,
                px0 + depth,
                py1
            )

        blockers = unary_union([

            s.polygon

            for s in state.spaces
        ])

        poly = poly.difference(
            blockers
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

        self._commit(

            state,

            "lawn",

            "lawn",

            poly,

            "environmental"
        )

        print(
            "  ✔ Lawn"
        )

    # =========================================================================
    # GREEN STRIPS
    # =========================================================================

    def place_side_green_strips(

        self,

        state
    ):

        px0, py0, px1, py1 = (
            state.plot_polygon.bounds
        )

        width = px1 - px0

        if width < 40:
            return

        strip = 4

        left = box(
            px0,
            py0 + 8,
            px0 + strip,
            py1 - 6
        )

        right = box(
            px1 - strip,
            py0 + 8,
            px1,
            py1 - 6
        )

        for idx, poly in enumerate([left, right]):

            self._commit(

                state,

                f"green_strip_{idx+1}",

                "green_strip",

                poly,

                "environmental"
            )

        print(
            "  ✔ Green strips"
        )

    # =========================================================================
    # BACKYARD
    # =========================================================================

    def place_backyard(

        self,

        state
    ):

        if "backyard" not in state.optional_rooms:
            return

        px0, py0, px1, py1 = (
            state.plot_polygon.bounds
        )

        facing = state.facing

        depth = 8

        if facing == "north":

            poly = box(
                px0 + 4,
                py0,
                px1 - 4,
                py0 + depth
            )

        elif facing == "south":

            poly = box(
                px0 + 4,
                py1 - depth,
                px1 - 4,
                py1
            )

        elif facing == "east":

            poly = box(
                px0,
                py0 + 4,
                px0 + depth,
                py1 - 4
            )

        else:

            poly = box(
                px1 - depth,
                py0 + 4,
                px1,
                py1 - 4
            )

        blockers = unary_union([

            s.polygon

            for s in state.spaces
        ])

        poly = poly.difference(
            blockers
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

        self._commit(

            state,

            "backyard",

            "backyard",

            poly,

            "environmental"
        )

        print(
            "  ✔ Rear backyard/service court"
        )

    # =========================================================================
    # COMMIT
    # =========================================================================

    def _commit(

        self,

        state,

        name,

        room_type,

        poly,

        zone
    ):

        if poly.is_empty:
            return

        poly = poly.buffer(0)

        space = Space(

            name=name,

            room_type=room_type,

            polygon=poly,

            zone=zone
        )

        state.spaces.append(
            space
        )