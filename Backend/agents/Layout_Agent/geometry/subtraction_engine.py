# =============================================================================
# SUBTRACTION ENGINE v20
# =============================================================================
# PURE RESIDUAL TOPOLOGY ENGINE
#
# FIXES
#
# ✔ topology collapse
# ✔ residual fragmentation
# ✔ invalid geometry propagation
# ✔ aggressive subtraction
# ✔ disappearing residuals
# ✔ unstable multi polygon handling
# ✔ environmental subtraction corruption
# ✔ living emergence starvation
#
# ARCHITECTURE
#
# buildable core
#       ↓
# progressive subtraction
#       ↓
# topology stabilization
#       ↓
# residual emergence
#
# =============================================================================

from shapely.geometry import (
    Polygon,
    MultiPolygon,
    GeometryCollection
)

from shapely.ops import unary_union

from state import LayoutState

# =============================================================================
# CONSTANTS
# =============================================================================

CUTTER_BUFFER = 0.02

MIN_FRAGMENT_AREA = 45.0

MIN_RESIDUAL_AREA = 120.0

GEOMETRY_FIX_BUFFER = 0.01

# =============================================================================
# ENGINE
# =============================================================================

class SubtractionEngine:

    # =========================================================================
    # INIT
    # =========================================================================

    def __init__(

        self,

        buildable_polygon,

        state: LayoutState
    ):

        self.state = state

        self.original = self._clean_geometry(
            buildable_polygon
        )

        self.remaining = self._clean_geometry(
            buildable_polygon
        )

        print("\n" + "=" * 60)
        print("SUBTRACTION ENGINE v20")
        print("=" * 60)

        print(
            f"  Initial Residual : "
            f"{self.remaining_area:.1f} sqft"
        )

    # =========================================================================
    # REMAINING AREA
    # =========================================================================

    @property
    def remaining_area(self):

        if self.remaining is None:
            return 0.0

        if self.remaining.is_empty:
            return 0.0

        return self.remaining.area

    # =========================================================================
    # REGION COUNT
    # =========================================================================

    @property
    def region_count(self):

        if self.remaining is None:
            return 0

        if self.remaining.is_empty:
            return 0

        if isinstance(
            self.remaining,
            MultiPolygon
        ):
            return len(
                self.remaining.geoms
            )

        return 1

    # =========================================================================
    # MAIN SUBTRACTION
    # =========================================================================

    def subtract(

        self,

        name,

        polygon
    ):

        # ---------------------------------------------------------------------
        # BASIC GUARDS
        # ---------------------------------------------------------------------

        if polygon is None:
            return False

        if self.remaining is None:
            return False

        if self.remaining.is_empty:
            return False

        # ---------------------------------------------------------------------
        # CLEAN CUTTER
        # ---------------------------------------------------------------------

        polygon = self._clean_geometry(
            polygon
        )

        if polygon is None:

            print(
                f"  [SUBTRACT] {name}"
                f" invalid geometry"
            )

            return False

        print(
            f"  [SUBTRACT] {name}"
        )

        # ---------------------------------------------------------------------
        # SOFT BUFFER
        # ---------------------------------------------------------------------

        try:

            cutter = polygon.buffer(
                CUTTER_BUFFER
            )

        except Exception as e:

            print(
                f"  [SUBTRACT] {name}"
                f" cutter failed: {e}"
            )

            return False

        cutter = self._clean_geometry(
            cutter
        )

        if cutter is None:
            return False

        # ---------------------------------------------------------------------
        # DIFFERENCE
        # ---------------------------------------------------------------------

        try:

            candidate = self.remaining.difference(
                cutter
            )

        except Exception as e:

            print(
                f"  [SUBTRACT] {name}"
                f" difference failed: {e}"
            )

            return False

        # ---------------------------------------------------------------------
        # CLEAN
        # ---------------------------------------------------------------------

        candidate = self._clean_geometry(
            candidate
        )

        if candidate is None:

            print(
                f"  [SUBTRACT] {name}"
                f" destroyed residual"
            )

            return False

        # ---------------------------------------------------------------------
        # SAFETY
        # ---------------------------------------------------------------------

        if candidate.area < MIN_RESIDUAL_AREA:

            print(
                f"  [SUBTRACT] {name}"
                f" residual too small"
            )

            return False

        # ---------------------------------------------------------------------
        # FINALIZE
        # ---------------------------------------------------------------------

        self.remaining = candidate

        print(
            f"             → "
            f"{self.remaining_area:.1f} sqft remaining"
        )

        return True

    # =========================================================================
    # SAFE INTERSECTION
    # =========================================================================

    def safe_intersection(

        self,

        polygon
    ):

        if polygon is None:
            return None

        if self.remaining is None:
            return None

        polygon = self._clean_geometry(
            polygon
        )

        if polygon is None:
            return None

        try:

            clipped = polygon.intersection(
                self.remaining
            )

        except Exception:

            return None

        clipped = self._clean_geometry(
            clipped
        )

        return clipped

    # =========================================================================
    # GET LARGEST RESIDUAL
    # =========================================================================

    def get_largest_residual(self):

        if self.remaining is None:
            return None

        if self.remaining.is_empty:
            return None

        if isinstance(
            self.remaining,
            MultiPolygon
        ):

            polygons = [

                p for p in self.remaining.geoms

                if p.area >= MIN_FRAGMENT_AREA
            ]

            if not polygons:
                return None

            return max(
                polygons,
                key=lambda g: g.area
            )

        return self.remaining

    # =========================================================================
    # CLEAN GEOMETRY
    # =========================================================================

    def _clean_geometry(

        self,

        geometry
    ):

        if geometry is None:
            return None

        if geometry.is_empty:
            return None

        # ---------------------------------------------------------------------
        # VALIDITY FIX
        # ---------------------------------------------------------------------

        try:

            geometry = geometry.buffer(
                GEOMETRY_FIX_BUFFER
            )

            geometry = geometry.buffer(
                -GEOMETRY_FIX_BUFFER
            )

            geometry = geometry.buffer(0)

        except Exception:
            return None

        if geometry.is_empty:
            return None

        # ---------------------------------------------------------------------
        # GEOMETRY COLLECTION
        # ---------------------------------------------------------------------

        if isinstance(
            geometry,
            GeometryCollection
        ):

            polygons = []

            for g in geometry.geoms:

                if isinstance(g, Polygon):

                    if g.area >= MIN_FRAGMENT_AREA:
                        polygons.append(g)

            if not polygons:
                return None

            geometry = unary_union(
                polygons
            )

        # ---------------------------------------------------------------------
        # MULTIPOLYGON
        # ---------------------------------------------------------------------

        if isinstance(
            geometry,
            MultiPolygon
        ):

            valid_parts = []

            for poly in geometry.geoms:

                if poly.area >= MIN_FRAGMENT_AREA:

                    valid_parts.append(
                        poly
                    )

            if not valid_parts:
                return None

            # -------------------------------------------------------------
            # KEEP MAJOR TOPOLOGY
            # -------------------------------------------------------------

            geometry = max(
                valid_parts,
                key=lambda p: p.area
            )

        # ---------------------------------------------------------------------
        # FINAL VALIDATION
        # ---------------------------------------------------------------------

        if geometry.area < MIN_FRAGMENT_AREA:
            return None

        if not geometry.is_valid:
            return None

        return geometry

    # =========================================================================
    # DEBUG
    # =========================================================================

    def debug(self):

        print("\n[RESIDUAL DEBUG]")

        print(
            f"  Remaining Area : "
            f"{self.remaining_area:.1f}"
        )

        print(
            f"  Regions        : "
            f"{self.region_count}"
        )

        if self.remaining is not None:

            minx, miny, maxx, maxy = (
                self.remaining.bounds
            )

            print(
                f"  Bounds         : "
                f"({minx:.1f}, {miny:.1f}) "
                f"→ "
                f"({maxx:.1f}, {maxy:.1f})"
            )