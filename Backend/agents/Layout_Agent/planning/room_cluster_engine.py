# =============================================================================
# ROOM CLUSTER ENGINE v25
# =============================================================================
# ARCHIVERSE — SEMANTIC SERVICE CLUSTER ORCHESTRATOR
# =============================================================================
# FIXES
#
# ✔ semantic kitchen anchoring
# ✔ kitchen strongly prefers SE
# ✔ rare NW fallback only
# ✔ utility touches external environmental edge
# ✔ utility outside kitchen
# ✔ wash beside utility
# ✔ dining circulation-aware
# ✔ dining attached to kitchen
# ✔ store inside kitchen
# ✔ store avoids SE stove corner
# ✔ all-facing support
# ✔ safer overlap validation
# ✔ residual-safe placement
#
# IMPORTANT
#
# store      -> INSIDE kitchen
# utility    -> OUTSIDE kitchen
# utility    -> MUST touch rear/open edge
# wash_area  -> beside utility
# dining     -> adjacent kitchen + living flow
#
# =============================================================================

import random

from shapely import area
from shapely.geometry import (
    box,
    MultiPolygon
)

from state import Space

from planning.plumbing_engine import PlumbingEngine

from planning.semantic_topology_rules import (
    SEMANTIC_RULES
)

# =============================================================================
# CONSTANTS
# =============================================================================

MIN_ROOM_AREA = 25

MIN_DIM = 5

ROOM_BUFFER = 0.05

SERVICE_GAP = 0.5

STORE_W = 4
STORE_H = 5

# =============================================================================
# ENGINE
# =============================================================================

class RoomClusterEngine:

    # =========================================================================
    # INIT
    # =========================================================================

    def __init__(

        self,

        engine,

        state,

        plumbing_engine=None
    ):

        self.engine = engine

        self.state = state

        self.plumbing_engine = plumbing_engine

        # =========================================================
        # BUILDABLE
        # =========================================================

        self.buildable = (
            state.buildable_polygon
        )

        self.bx0, self.by0, self.bx1, self.by1 = (

            self.buildable.bounds
        )

        # =========================================================
        # FULL PLOT
        # =========================================================

        self.plot_polygon = (
            state.plot_polygon
        )

        self.px0, self.py0, self.px1, self.py1 = (

            self.plot_polygon.bounds
        )

        # =========================================================
        # FACING
        # =========================================================

        self.facing = (
            state.facing.lower()
        )

        # =========================================================
        # DYNAMIC BUILDABLE
        # =========================================================

        self.build_width = (

            self.bx1 - self.bx0
        )

        self.build_height = (

            self.by1 - self.by0
        )

        # =========================================================
        # ALIASES
        # =========================================================

        self.buildable_width = (
            self.build_width
        )

        self.buildable_height = (
            self.build_height
        )

        # =========================================================
        # ASPECT
        # =========================================================

        self.aspect_ratio = (

            self.build_width

            /

            max(self.build_height, 1)
        )
         

    # =========================================================================
    # SERVICE CLUSTER
    # =========================================================================

    def place_service_cluster(

        self,

        room_plan
    ):

        print("\n[SERVICE CLUSTER]")

        kitchen = self._find_plan(
            room_plan,
            "kitchen"
        )

        if kitchen is None:
            return

        kitchen_space = self._place_kitchen(
            kitchen
        )

        if kitchen_space is None:
            return

        # ---------------------------------------------------------------------
        # STORE
        # ---------------------------------------------------------------------

        store = self._find_plan(
            room_plan,
            "store"
        )

        if store:

            self._place_store(
                kitchen_space,
                store
            )

        # ---------------------------------------------------------------------
        # UTILITY
        # ---------------------------------------------------------------------

        utility = self._find_plan(
            room_plan,
            "utility"
        )

        utility_space = None

        if utility:

            utility_space = self._place_utility(
                kitchen_space,
                utility
            )

        # ---------------------------------------------------------------------
        # WASH AREA
        # ---------------------------------------------------------------------

        wash = self._find_plan(
            room_plan,
            "wash_area"
        )

        if wash and utility_space:

            self._place_wash_area(
                utility_space,
                wash
            )

    # =========================================================================
    # SOCIAL CLUSTERS
    # =========================================================================

    def place_social_clusters(

        self,

        room_plan
    ):

        print("\n[SOCIAL CLUSTERS]")

        dining = self._find_plan(
            room_plan,
            "dining"
        )

        if dining:

            self._place_dining(
                dining
            )

    # =========================================================================
    # KITCHEN
    # STRICT SOUTH-EAST PRIORITY
    # =============================================================================
    #
    # PRIORITY
    #
    # 1. SOUTH EAST (ALWAYS)
    # 2. VERY RARE NORTH WEST FALLBACK
    #
    # NEVER:
    # ✘ SOUTH WEST
    #
    # RULES
    #
    # ✔ use BUILDABLE bounds
    # ✔ touch external edge
    # ✔ south-facing must touch parking edge
    # ✔ larger realistic sizing
    # ✔ true service corner lock
    #
    # =============================================================================

    def _place_kitchen(

        self,

        room
    ):

        # ---------------------------------------------------------------------
        # IMPORTANT
        # USE BUILDABLE AREA
        # NOT FULL PLOT
        # ---------------------------------------------------------------------

        buildable = (

            self.state
            .buildable_polygon
            .buffer(-0.2)
        )

        bx0, by0, bx1, by1 = (
            buildable.bounds
        )

        # ---------------------------------------------------------------------
        # ADAPTIVE KITCHEN SIZE
        # ---------------------------------------------------------------------

        scale = getattr(

            self.state,

            "kitchen_scale_bias",

            1.35
        )

        w = max(

            room["width"] * scale - 1.5,

            13
        )

        h = max(

            room["height"] * scale * 0.82 - 1.0,

            10
        )
        
        vs = self.variant_scale()

        w *= vs
        h *= vs

        # ---------------------------------------------------------------------
        # UPSCALE FOR LARGER BUILDABLE
        # ---------------------------------------------------------------------

        area = self.buildable.area

        if area > 1400:

            w += 2
            h += 2

        if area > 2000:

            w += 3
            h += 3

        if area > 2800:

            w += 4
            h += 4

        candidates = []

        # =========================================================================
        # NORTH FACING
        #
        # ROAD = NORTH
        # SERVICE = SOUTH-EAST
        # =========================================================================

        if self.facing == "north":

            se_candidate = box(

                bx1 - w,
                by0,

                bx1,
                by0 + h
            )

            candidates.append(
                se_candidate
            )

        # =========================================================================
        # SOUTH FACING
        #
        # ROAD = SOUTH
        # TRUE SE BUILDABLE CORNER
        #
        # MUST:
        # ✔ touch east boundary
        # ✔ touch south boundary
        # ✔ align parking edge
        # =========================================================================

        elif self.facing == "south":

            # -------------------------------------------------------------
            # SOUTH FACING
            #
            # BEST TOPOLOGY:
            #
            # ✔ kitchen in NORTH-WEST
            # ✔ dining adjacent east
            # ✔ utility/wash in SE strip
            # ✔ avoids parking conflict
            # ✔ preserves circulation
            # -------------------------------------------------------------

            nw_candidate = box(

                bx0,
                by1 - h,

                bx0 + w,
                by1
            )

            candidates.append(
                nw_candidate
            )

        # =========================================================================
        # EAST FACING
        #
        # ROAD = EAST
        # SERVICE = SOUTH-WEST/SE
        # prefer SE service cluster
        # =========================================================================

        elif self.facing == "east":

            se_candidate = box(

                bx1 - w,
                by0,

                bx1,
                by0 + h
            )

            candidates.append(
                se_candidate
            )

        # =========================================================================
        # WEST FACING
        #
        # ROAD = WEST
        # SERVICE = SOUTH-EAST
        # =========================================================================

        else:

            se_candidate = box(

                bx1 - w,
                by0,

                bx1,
                by0 + h
            )

            candidates.append(
                se_candidate
            )

        # ---------------------------------------------------------------------
        # VERY RARE NW FALLBACK
        # ONLY USED IF SE FAILS
        # ---------------------------------------------------------------------

        nw_candidate = box(

            bx0,
            by1 - h,

            bx0 + w,
            by1
        )

        candidates.append(
            nw_candidate
        )

        # =========================================================================
        # TRY CANDIDATES
        # =========================================================================

        for idx, candidate in enumerate(
            candidates
        ):

            poly = self.engine.safe_intersection(
                candidate
            )

            if poly is None:
                continue

            if poly.is_empty:
                continue

            # -----------------------------------------------------------------
            # VALIDATE TRUE SE POSITION
            # -----------------------------------------------------------------

            minx, miny, maxx, maxy = (
                poly.bounds
            )

            center_x = (
                (minx + maxx) / 2
            )

            center_y = (
                (miny + maxy) / 2
            )

            build_center_x = (
                (bx0 + bx1) / 2
            )

            build_center_y = (
                (by0 + by1) / 2
            )

            # -----------------------------------------------------------------
            # FORCE TRUE SE
            # except rare fallback
            # -----------------------------------------------------------------

            if idx == 0:

                is_se = (

                    center_x > build_center_x

                    and

                    center_y < build_center_y
                )

                if not is_se:
                    continue

                # -------------------------------------------------------------
                # IMPORTANT
                # FORCE EXTERNAL EDGE TOUCH
                # -------------------------------------------------------------

                touches_east = (
                    abs(maxx - bx1) < 1.0
                )

                touches_south = (
                    abs(miny - by0) < 1.0
                )

                if not (
                    touches_east
                    and
                    touches_south
                ):
                    continue

            placed = self._commit(

                room,
                poly,
                "service"
            )

            if placed:

                if idx == 0:

                    print(
                        "  ✔ kitchen strict SE buildable anchor"
                    )

                else:

                    print(
                        "  ✔ kitchen rare NW fallback"
                    )

                return placed

        return None

    

    # =========================================================================
    # STORE INSIDE KITCHEN
    # avoids SE stove corner
    # =========================================================================

    def _place_store(

        self,

        kitchen,

        room
    ):

        kx0, ky0, kx1, ky1 = (
            kitchen.polygon.bounds
        )

        w = room["width"]
        h = room["height"]

        # ---------------------------------------------------------
        # INSIDE KITCHEN CORNER
        # ---------------------------------------------------------

        poly = box(

            kx1 - w,
            ky1 - h,

            kx1,
            ky1
        )

        placed = self._commit(

            room,
            poly,
            "service"
        )

        if placed:

            print(
                "  ✔ store inside kitchen"
            )

        return placed

    # =========================================================================
    # UTILITY
    # outside buildable boundary
    # =========================================================================

    def _place_utility(
        self,
        kitchen_space,
        room
    ):

        from shapely.geometry import box

        kx0, ky0, kx1, ky1 = (
            kitchen_space.polygon.bounds
        )
        
        # =========================================================
        # GET BACKYARD FIRST
        # =========================================================

        backyard = self.state.get_space("backyard")

        if backyard is None:
            return None

        bbx0, bby0, bbx1, bby1 = (
            backyard.polygon.bounds
        )
        
        # =========================================================
        # NORTH
        # utility BETWEEN kitchen + backyard
        # =========================================================

        if self.facing == "north":

            util_w = 6
            util_h = 5

            # utility in rear setback
            # touching backyard RIGHT edge
            # touching kitchen SOUTH strip

            ux0 = bbx1
            ux1 = ux0 + util_w

            uy0 = self.py0
            uy1 = uy0 + util_h

        # =========================================================
        # EAST
        # utility in SOUTH setback
        # =========================================================

        elif self.facing == "east":

            util_w = 4
            util_h = 3

            lawn = self.state.get_space("front_lawn")

            if lawn:
                lx0, ly0, lx1, ly1 = lawn.polygon.bounds
            else:
                lx0, ly0, lx1, ly1 = (
                    self.bx1,
                    self.by0,
                    self.px1,
                    self.by1
                )

            # ------------------------------------------------
            # OUTSIDE kitchen
            # touching lawn boundary
            # placed in east setback strip
            # ------------------------------------------------

            ux1 = lx0
            ux0 = ux1 - util_w

            # BELOW kitchen boundary
            uy1 = kitchen_space.polygon.bounds[1]
            uy0 = uy1 - util_h
        # =========================================================
        # SOUTH
        # utility touches backyard + kitchen
        # =========================================================

        elif self.facing == "south":

            util_w = 6
            util_h = 5

            # rear setback strip
            # touching backyard LEFT edge

            ux1 = bbx0
            ux0 = ux1 - util_w

            uy1 = self.py1
            uy0 = uy1 - util_h

        # =========================================================
        # WEST
        # existing working logic
        # =========================================================

        else:

            util_w = self.px1 - self.bx1
            util_h = 6

            ux0 = self.bx1
            ux1 = self.px1

            uy0 = ky0
            uy1 = uy0 + util_h

        utility_poly = box(
            ux0,
            uy0,
            ux1,
            uy1
        )

        placed = self._commit(
            room,
            utility_poly,
            "service"
        )

        return placed


    # =========================================================================
    # WASH AREA
    # beside utility
    # =========================================================================

    def _place_wash_area(
        self,
        utility,
        room
    ):

        from shapely.geometry import box

        ux0, uy0, ux1, uy1 = (
            utility.polygon.bounds
        )

        util_w = ux1 - ux0
        util_h = uy1 - uy0

        # =====================================================
        # NORTH
        # wash beside utility horizontally
        # =====================================================
        if self.facing == "north":

            wash_w = 5
            wash_h = util_h

            wx0 = ux1
            wx1 = wx0 + wash_w

            wy0 = uy0
            wy1 = uy1


        # =====================================================
        # SOUTH
        # wash beside utility horizontally
        # =====================================================
        elif self.facing == "south":

            wash_w = 5
            wash_h = util_h

            wx1 = ux0
            wx0 = wx1 - wash_w

            wy0 = uy0
            wy1 = uy1


        # =====================================================
        # EAST
        # wash ABOVE utility
        # =====================================================
        elif self.facing == "east":

            wash_w = 4
            wash_h = 3

            # wash | utility
            # horizontal placement

            wx1 = ux0
            wx0 = wx1 - wash_w

            wy0 = uy0
            wy1 = wy0 + wash_h


        # =====================================================
        # WEST
        # existing perfect logic
        # =====================================================
        else:

            wash_h = 4

            wx0 = ux0
            wx1 = ux1

            wy0 = uy1
            wy1 = wy0 + wash_h

        wash_poly = box(
            wx0,
            wy0,
            wx1,
            wy1
        )

        placed = self._commit(
            room,
            wash_poly,
            "service"
        )

        return placed
 
    # =========================================================================
    # DINING
    # circulation-aware
    # kitchen-adjacent
    # living-facing
    # =========================================================================
    def _place_dining(

        self,

        room
    ):

        kitchen = self.state.get_space(
            "kitchen"
        )

        if kitchen is None:
            return

        buildable = (
            self.state.buildable_polygon
        )

        bx0, by0, bx1, by1 = (
            buildable.bounds
        )

        w = room["width"]
        h = room["height"]
        
        vs = self.variant_scale()

        w *= vs
        h *= vs
                
        area = self.buildable.area

        if area > 1600:

            w += 2
            h += 1

        if area > 2400:

            w += 3
            h += 2

        if area > 3200:

            w += 4
            h += 3

        kx0, ky0, kx1, ky1 = (
            kitchen.polygon.bounds
        )

        # =====================================================
        # NORTH / SOUTH
        # dining ABOVE kitchen
        # =====================================================

        if self.facing in (

            "north",
            "south"
        ):

            dw = max(
                w,
                (kx1 - kx0) * 0.95
            )

            # -------------------------------------------------
            # ALIGN WITH KITCHEN
            # -------------------------------------------------

            dx0 = kx0
            dx1 = min(
                bx1 - 0.1,
                dx0 + dw
            )

            if self.facing == "north":

                dx0 = kx0
                dx1 = kx1

                dy0 = ky1
                dy1 = dy0 + h

            # =================================================
            # SOUTH
            # dining below kitchen
            # =================================================

            # =================================================
            # SOUTH
            #
            # dining between master + secondary
            # =================================================

            else:

                dx0 = kx0
                dx1 = kx1

                dy1 = ky0
                dy0 = dy1 - h

        # =====================================================
        # EAST / WEST
        # dining above kitchen
        # =====================================================

        else:

            dx0 = kx0
            dx1 = kx1

            dy0 = ky1
            dy1 = dy0 + h

        # =====================================================
        # FINAL POLY
        # =====================================================

        poly = box(

            dx0,
            dy0,

            dx1,
            dy1
        )

        poly = poly.buffer(0)

        placed = self._commit(

            {
                **room,
                "embedded": True,
                "allow_overlap": True
            },

            poly,

            "social"
        )

        if placed:

            print(
                "  ✔ dining corrected-anchor"
            )

        return placed
    
    
    
    

# =========================================================================
# BEDROOM PLACEMENT
# =========================================================================

    # =============================================================================
    # ROOM CLUSTER ENGINE
    # ADD THIS INSIDE place_bedrooms()
    # =============================================================================

    def place_bedrooms(

        self,

        bedrooms_required
    ):

        secondary_count = max(
            0,
            bedrooms_required - 1
        )

        # =====================================================
        # NORTH
        # =====================================================

        if self.facing == "north":

            master = self._north_master()

            if master:
                self._place_attached_bath(master)

            secondaries = self._north_secondary(
                secondary_count
            )

            for s in secondaries:

                self._place_attached_bath(s)

        # =====================================================
        # EAST
        # =====================================================

        elif self.facing == "east":

            master = self._east_master()

            if master:
                self._place_attached_bath(master)

            secondaries = self._east_secondary(
                secondary_count
            )

            for s in secondaries:

                self._place_attached_bath(s)

        # =====================================================
        # SOUTH
        # =====================================================

        elif self.facing == "south":

            master = self._south_master()

            if master:
                self._place_attached_bath(master)

            secondaries = self._south_secondary(
                secondary_count
            )

            for s in secondaries:

                self._place_attached_bath(s)

        # =====================================================
        # WEST
        # =====================================================

        else:

            master = self._west_master()

            if master:
                self._place_attached_bath(master)

            secondaries = self._west_secondary(
                secondary_count
            )

            for s in secondaries:

                self._place_attached_bath(s)
            
            
    def add_secondary_bedroom(
        self,
        poly
    ):

        poly = self.normalize_room_gap(
            poly
        )

        # keep inside buildable
        poly = poly.intersection(
            self.state.buildable_polygon
        )

        if poly.is_empty:
            return None

        if poly.area < 80:
            return None

        self.add_secondary_bedroom(
            poly
        )

    # =========================================================================
    # NORTH FACING
    # =========================================================================
    #
    # MASTER:
    #   SW
    #
    # SECONDARY:
    #   NE touching parking OR dining
    #   NW touching buildable boundary
    #
    # =========================================================================

    def _north_master(self):

        bw = self.buildable_width
        bh = self.buildable_height

        w = max(13, bw * 0.36)
        h = max(14, bh * 0.30)

        vs = self.variant_scale()

        w *= vs
        h *= vs

        # -------------------------------------------------
        # ALWAYS TOUCH WEST + SOUTH
        # -------------------------------------------------

        x0 = self.bx0
        y0 = self.by0



        poly = box(
            x0,
            y0,
            x0 + w,
            y0 + h
        )
        poly = self.normalize_room_gap(
            poly
        )
        return self.add_room(
            "master_bedroom",
            poly
        )

        if placed:

            self._place_attached_bath(
                placed
            )

    def _north_secondary(
        self,
        secondary_count
    ):

        dining = self.state.get_space(
            "dining"
        )

        if dining is None:
            return

        dx0, dy0, dx1, dy1 = (
            dining.polygon.bounds
        )

        if secondary_count >= 1:

            w = 12
            h = 12

            x1 = self.bx1
            x0 = x1 - w

            y0 = dy1
            y1 = y0 + h

            if y1 > self.by1 - 1:

                y1 = self.by1 - 1
                y0 = y1 - h

            poly = box(
                x0,
                y0,
                x1,
                y1
            )

            poly = self.normalize_room_gap(
                poly
            )

            self.add_secondary_bedroom(
                poly
            )
    # =========================================================================
    # EAST FACING
    # =========================================================================
    #
    # MASTER:
    #   SW
    #   may touch kitchen
    #   OR leave 2ft
    #
    # SECONDARY:
    #   NW
    #   scalable
    #
    # =========================================================================
    def _east_master(self):

        kitchen = self.state.get_space("kitchen")

        w, h = self.scale_room_size(13, 14)

        vs = self.variant_scale()

        w *= vs
        h *= vs

        # ============================================
        # SOUTH-WEST
        # ============================================

        x0 = self.bx0
        y0 = self.by0

        # ============================================
        # OPTIONAL 2-3FT GAP FROM KITCHEN
        # ============================================

        if kitchen:

            kx0, ky0, kx1, ky1 = (
                kitchen.polygon.bounds
            )

            proposed_x1 = x0 + w

            gap = kx0 - proposed_x1

            # ----------------------------------------
            # if tiny gap -> TOUCH kitchen
            # ----------------------------------------

            if gap < 3:

                w = kx0 - x0

            # ----------------------------------------
            # else preserve 2-3ft gap
            # ----------------------------------------

            else:

                w = min(
                    w,
                    (kx0 - x0) - 2.5
                )

        poly = box(
            x0,
            y0,
            x0 + w,
            y0 + h
        )

        poly = self.normalize_room_gap(poly)

        
        
        self.add_secondary_bedroom(
            poly
        )
        
        return self.add_room(
            "master_bedroom",
            poly
        )
        
        
    def _east_secondary(
        self,
        secondary_count
    ):

        if secondary_count < 1:
            return

        w = 14
        h = 15

        x0 = self.bx0
        y1 = self.by1
        y0 = y1 - h

        poly = box(
            x0,
            y0,
            x0 + w,
            y1
        )

        poly = self.normalize_room_gap(
            poly
        )

        self.add_secondary_bedroom(
            poly
        )
    # =========================================================================
    # SOUTH FACING
    # =========================================================================
    #
    # MASTER:
    #   NE
    #
    # SECONDARY:
    #   SE or SW
    #   touching boundary
    #
    # DINING:
    #   between master + secondary
    #
    # =========================================================================

    def _south_master(self):

        w = 16
        h = 19

        x0 = self.bx1 - w
        y0 = self.by1 - h

        poly = box(
            x0,
            y0,
            x0 + w,
            y0 + h
        )

        poly = self.normalize_room_gap(
            poly
        )

        return self.add_room(
            "master_bedroom",
            poly
        )

        if placed:

            self._place_attached_bath(
                placed
            )
            
    def _south_secondary(
        self,
        secondary_count
    ):

        kitchen = self.state.get_space(
            "kitchen"
        )

        if kitchen is None:
            return

        kx0, ky0, kx1, ky1 = (
            kitchen.polygon.bounds
        )

        # =====================================================
        # SOUTH-WEST SECONDARY
        # =====================================================

        if secondary_count >= 1:

            w = 16
            h = 14

            vs = self.variant_scale()

            w *= vs
            h *= vs

            x0 = self.bx0

            # BELOW kitchen
            y1 = ky0
            y0 = y1 - h

            # snap south
            if y0 < self.by0:

                y0 = self.by0
                y1 = y0 + h

            poly = box(
                x0,
                y0,
                x0 + w,
                y1
            )

            poly = self.normalize_room_gap(
                poly
            )

            self.add_secondary_bedroom(
                poly
            )
            
        if secondary_count >= 2:

            dining = self.state.get_space(
                "dining"
            )

            if dining is None:
                return

            dx0, dy0, dx1, dy1 = (
                dining.polygon.bounds
            )

            w = 14
            h = 13

            x0 = self.bx1 - w

            # ABOVE DINING
            y0 = dy1

            # SNAP NORTH
            if y0 + h > self.by1:

                y0 = self.by1 - h

            poly = box(
                x0,
                y0,
                x0 + w,
                y0 + h
            )

            self.add_secondary_bedroom(
                poly
            )

            self._place_attached_bath(
                self.state.spaces[-1]
            )
            

    # =========================================================================
    # WEST FACING
    # =========================================================================
    #
    # MASTER:
    #   SE beside kitchen
    #   touching stair + lawn boundary
    #
    # SECONDARY:
    #   NE
    #   east side
    #
    # =========================================================================

    def _west_master(self):

        w, h = self.scale_room_size(13, 15)

        vs = self.variant_scale()

        w *= vs
        h *= vs

        # ============================================
        # NORTH-EAST CORNER
        # ============================================

        x0 = self.bx1 - w
        y0 = self.by1 - h

        poly = box(
            x0,
            y0,
            x0 + w,
            y0 + h
        )

        poly = self.normalize_room_gap(
            poly
        )

        return self.add_room(

            "master_bedroom",

            poly
        )
        

    def _west_secondary(

        self,
        secondary_count
    ):

        kitchen = self.state.get_space(
            "kitchen"
        )

        if kitchen is None:
            return

        kx0, ky0, kx1, ky1 = (
            kitchen.polygon.bounds
        )

        # =====================================================
        # BEDROOM 1
        # WEST OF KITCHEN
        # =====================================================

        if secondary_count >= 1:

            w = 16
            h = 13

            x1 = kx0
            x0 = x1 - w

            if x0 < self.bx0:

                x0 = self.bx0
                x1 = x0 + w

            y0 = self.by0

            poly = box(
                x0,
                y0,
                x1,
                y0 + h
            )

            self.add_secondary_bedroom(
                poly
            )

            self._place_attached_bath(
                self.state.spaces[-1]
            )

        # =====================================================
        # BEDROOM 2
        # ABOVE DINING
        # =====================================================

        if secondary_count >= 2:

            dining = self.state.get_space(
                "dining"
            )

            if dining is None:
                return

            dx0, dy0, dx1, dy1 = (
                dining.polygon.bounds
            )

            w = 14
            h = 13

            x0 = self.bx1 - w
            y0 = self.by1 - h

            poly = box(
                x0,
                y0,
                x0 + w,
                y0 + h
            )

            self.add_secondary_bedroom(
                poly
            )

            self._place_attached_bath(
                self.state.spaces[-1]
            )
            
    def add_secondary_bedroom(
        self,
        poly
    ):

        poly = self.normalize_room_gap(
            poly,
            threshold=1.2
        )

        poly = poly.intersection(
            self.state.buildable_polygon
        )

        if poly.is_empty:
            return None

        if poly.area < 80:
            return None

        placed = self.add_room(
            "bedroom",
            poly
        )

        # =====================================================
        # ATTACHED BATH
        # =====================================================

        if placed:

            self._place_attached_bath(
                placed
            )

            try:
                self.engine.occupied.append(
                    poly
                )
            except:
                pass

        return placed
    
    def _place_attached_bath(

        self,

        bedroom_space
    ):

        if bedroom_space is None:
            return

        bath_w = 5
        bath_h = 7

        if self.facing == "north":

            preferred = "north-east"

        elif self.facing == "south":

            preferred = "north-west"

        elif self.facing == "east":

            preferred = "south-west"

        else:

            preferred = "south-east"

        bath_poly = (

            self.plumbing_engine
            ._internal_bathroom(

                bedroom_space.polygon,

                bath_w,

                bath_h,

                preferred
            )
        )

        if bath_poly is None:
            return

        self.add_room(
            "bathroom",
            bath_poly
        )
                
# =========================================================================
# protected
# =========================================================================

    def _get_service_protected_zone(self):

        facing = self.state.facing.lower()

        margin = 12

        if facing == "north":

            return box(

                self.bx1 - margin,
                self.by0,

                self.bx1,
                self.by0 + margin
            )

        elif facing == "south":

            return box(

                self.bx0,
                self.by1 - margin,

                self.bx0 + margin,
                self.by1
            )

        elif facing == "east":

            return box(

                self.bx0,
                self.by0,

                self.bx0 + margin,
                self.by0 + margin
            )

        return box(

            self.bx1 - margin,
            self.by0,

            self.bx1,
            self.by0 + margin
        )


    # =========================================================================
    # ADD ROOM
    # =========================================================================

    def add_room(

        self,

        room_type,

        polygon
    ):

        room = {

            "name": room_type,

            "type": room_type,

            "width": polygon.bounds[2] - polygon.bounds[0],

            "height": polygon.bounds[3] - polygon.bounds[1]
        }

        zone = "private"

        if room_type in {

            "kitchen",
            "store",
            "utility",
            "wash_area"
        }:

            zone = "service"

        elif room_type in {

            "dining",
            "living"
        }:

            zone = "social"

        return self._commit(

            room,
            polygon,
            zone
        )
        
    def snap_to_boundary(
        self,
        x0,
        y0,
        w,
        h,
        side
    ):

        if side == "north":
            y0 = self.by1 - h

        elif side == "south":
            y0 = self.by0

        elif side == "east":
            x0 = self.bx1 - w

        elif side == "west":
            x0 = self.bx0
        
        
    def scale_room_size(
        self,
        base_w,
        base_h
    ):

        area = self.buildable.area

        scale = 1.0

        if area > 1800:
            scale = 1.15

        if area > 2400:
            scale = 1.30

        if area > 3200:
            scale = 1.45

        return (
            base_w * scale,
            base_h * scale
        )
    # =========================================================================
    # COMMIT
    # =========================================================================

    def _commit(

        self,

        room,

        polygon,

        zone
    ):

        if polygon is None:
            return None

        if polygon.is_empty:
            return None

        polygon = polygon.buffer(0)
        
        polygon = self.normalize_room_gap(
            polygon,
            threshold=3
        )

        current = room["type"]

        SERVICE_TYPES = {

            "store",
            "utility",
            "wash_area"
        }

        # =====================================================
        # NORMAL ROOMS
        # =====================================================

        if current not in SERVICE_TYPES:

            if polygon.area < MIN_ROOM_AREA:

                return None

        # =====================================================
        # SERVICE STRIPS
        # =====================================================

        else:

            if polygon.area < 6:

                return None

        minx, miny, maxx, maxy = (
            polygon.bounds
        )

        width = maxx - minx
        height = maxy - miny

        # =========================================================
        # SERVICE ROOMS CAN USE SETBACK WIDTH
        # =========================================================

        SERVICE_TYPES = {
            "store",
            "utility",
            "wash_area"
        }

        if room["type"] not in SERVICE_TYPES:

            if min(width, height) < MIN_DIM:
                return None

        else:

            # allow narrow setback service strips

            if min(width, height) < 2.5:
                return None

        # =========================================================
        # VALID EMBEDDED RELATIONS
        # =========================================================

        ALLOW_TOUCHING = {

            ("store", "kitchen"),
            ("utility", "kitchen"),
            ("wash_area", "utility"),
            ("wash_area", "kitchen"),
            ("dining", "living"),
            ("dining", "kitchen"),

            ("bathroom", "master_bedroom"),
            ("master_bedroom", "bathroom"),

            ("bathroom", "bedroom"),
            ("bedroom", "bathroom"),
            
            ("living", "dining"),
            ("dining", "living"),
        }

        current = room["type"]

        allow_overlap = room.get(
            "allow_overlap",
            False
        )

        embedded = room.get(
            "embedded",
            False
        )

        # =====================================================
        # OVERLAP CHECK
        # =====================================================

        OUTDOOR_TYPES = {

            "backyard",
            "green_strip",
            "front_lawn",
            "lawn"
        }

        SERVICE_TYPES = {

            "store",
            "utility",
            "wash_area"
        }

        for s in self.state.spaces:

            try:

                existing = s.room_type

                # =====================================================
                # VALID TOUCHING RELATIONS
                # =====================================================

                if (
                    current,
                    existing
                ) in ALLOW_TOUCHING:

                    continue

                if (
                    existing,
                    current
                ) in ALLOW_TOUCHING:

                    continue

                inter = polygon.intersection(
                    s.polygon
                )

                if inter.is_empty:
                    continue

                inter_area = inter.area

                # =====================================================
                # ONLY shared-edge touching allowed
                # =====================================================

                if inter_area <= 0.05:
                    continue

                # =====================================================
                # utility/wash CAN EXIST INSIDE setbacks
                # but backyard can NEVER cut them
                # =====================================================

                # ---------------------------------------------------------
                # utility/wash can exist in EAST lawn setback strip
                # ---------------------------------------------------------

                if (

                    current in {
                        "utility",
                        "wash_area"
                    }

                    and

                    existing in OUTDOOR_TYPES
                ):

                    # EAST facing:
                    # allow utility/wash inside front lawn strip

                    if self.facing == "east":

                        continue

                    return None

                if (

                    current in OUTDOOR_TYPES

                    and

                    existing in {
                        "utility",
                        "wash_area"
                    }
                ):

                    return None

                # =====================================================
                # NORMAL ROOM COLLISION
                # =====================================================

                if current not in SERVICE_TYPES:

                    if inter_area > 0.5:
                        return None

                # =====================================================
                # SERVICE ROOM COLLISION
                # =====================================================

                else:

                    # =====================================================
                    # BEDROOM FLEX OVERLAP FIX
                    # =====================================================

                    if current in {
                        "bedroom",
                        "master_bedroom"
                    }:

                        # allow tiny edge touching only
                        if inter_area < 1.2:
                            continue

                        return None

                    if inter_area > 0.5:
                        return None

            except Exception:

                continue

        # =========================================================
        # PROTECTED SERVICE EDGE
        # =========================================================

        protected = self._get_service_protected_zone()

        if zone == "outdoor":

            try:

                if polygon.intersects(protected):

                    return None

            except:
                pass

        # =========================================================
        # CREATE SPACE
        # =========================================================

        space = Space(

            name=room["name"],

            room_type=current,

            polygon=polygon,

            zone=zone
        )

        self.state.spaces.append(
            space
        )
        
        # =========================================================
        # SERVICE STRIPS SHOULD NEVER SUBTRACT
        # =========================================================

        NON_SUBTRACT_TYPES = {

            "utility",
            "wash_area",
            "backyard",
            "green_strip",
            "front_lawn"
        }

        NO_SUBTRACT_ROOMS = {

            "bedroom",
            "master_bedroom"
        }

        if (

            current not in NON_SUBTRACT_TYPES

            and

            current not in NO_SUBTRACT_ROOMS
        ):

            try:

                self.engine.subtract(
                    room["name"],
                    polygon
                )

            except Exception:

                pass

        print(

            f"  ✔ {room['name']:18s}"

            f"{polygon.area:.1f} sqft"
        )

        return space
    # =========================================================================
    # FIND PLAN
    # =========================================================================

    def _find_plan(

        self,

        room_plan,

        room_type
    ):

        for r in room_plan:

            if r["type"] == room_type:
                return r

        return None
    
    def variant_scale(self):

        return 1.0
    
    def normalize_room_gap(
        self,
        poly,
        threshold=1.2
    ):

        minx, miny, maxx, maxy = poly.bounds

        # =====================================================
        # LEFT
        # =====================================================

        if abs(minx - self.bx0) < threshold:

            minx = self.bx0

        # =====================================================
        # RIGHT
        # =====================================================

        if abs(self.bx1 - maxx) < threshold:

            maxx = self.bx1

        # =====================================================
        # BOTTOM
        # =====================================================

        if abs(miny - self.by0) < threshold:

            miny = self.by0

        # =====================================================
        # TOP
        # =====================================================

        if abs(self.by1 - maxy) < threshold:

            maxy = self.by1

        return box(
            minx,
            miny,
            maxx,
            maxy
        )
        
    def _place_living(

        self,

        room
    ):

        dining = self.state.get_space(
            "dining"
        )

        if dining is None:
            return None

        dx0, dy0, dx1, dy1 = (
            dining.polygon.bounds
        )

        # =====================================================
        # DYNAMIC SIZE
        # =====================================================

        w = max(
            room["width"],
            self.buildable_width * 0.42
        )

        h = max(
            room["height"],
            self.buildable_height * 0.30
        )

        # =====================================================
        # NORTH
        # dining below living
        # =====================================================

        if self.facing == "north":

            lx0 = dx0 - 4
            lx1 = lx0 + w

            ly0 = dy1
            ly1 = ly0 + h

        # =====================================================
        # SOUTH
        # living below dining
        # =====================================================

        elif self.facing == "south":

            lx0 = dx0 - 4
            lx1 = lx0 + w

            ly1 = dy0
            ly0 = ly1 - h

        # =====================================================
        # EAST
        # living west of dining
        # =====================================================

        elif self.facing == "east":

            lx1 = dx0
            lx0 = lx1 - w

            ly0 = dy0 - 2
            ly1 = ly0 + h

        # =====================================================
        # WEST
        # living east of dining
        # =====================================================

        else:

            lx0 = dx1
            lx1 = lx0 + w

            ly0 = dy0 - 2
            ly1 = ly0 + h

        # =====================================================
        # BUILDABLE CLAMP
        # =====================================================

        if lx0 < self.bx0:
            lx0 = self.bx0

        if lx1 > self.bx1:
            lx1 = self.bx1

        if ly0 < self.by0:
            ly0 = self.by0

        if ly1 > self.by1:
            ly1 = self.by1

        poly = box(
            lx0,
            ly0,
            lx1,
            ly1
        )

        # =====================================================
        # MERGE FEEL
        # =====================================================

        poly = poly.buffer(0)

        placed = self._commit(

            {
                **room,
                "embedded": True,
                "allow_overlap": True
            },

            poly,

            "social"
        )

        if placed:

            print(
                "  ✔ merged living+dining"
            )

        return placed