# # =============================================================================
# # boundary_manager.py
# # =============================================================================
# # ARCHIVERSE — BOUNDARY MANAGER v10
# # =============================================================================
# # FIXES
# #
# # ✔ subtracts walkway setback correctly
# # ✔ strict outdoor → indoor topology
# # ✔ buildable starts AFTER:
# #       green strip
# #       walkway
# #       backyard
# #       frontage
# #
# # ✔ cleaner dashed buildable boundary
# # ✔ no outdoor/buildable overlap
# # ✔ safer geometry cleanup
# # ✔ stable subtraction ordering
# #
# # =============================================================================

# from typing import List
# from typing import Optional

# from shapely.geometry import (
#     Polygon,
#     MultiPolygon,
#     box
# )

# from shapely.ops import unary_union

# # =============================================================================
# # CONSTANTS
# # =============================================================================

# MIN_BUILDABLE_AREA = 180.0

# MIN_FRAGMENT_AREA = 80.0

# GEOMETRY_BUFFER = 0.01

# DEFAULT_FRONT_SETBACK = 4.0
# DEFAULT_SIDE_SETBACK  = 3.0
# DEFAULT_REAR_SETBACK  = 5.0

# # =============================================================================
# # PLOT CREATION
# # =============================================================================

# def create_plot_boundary(

#     width: float,

#     height: float
# ) -> Polygon:

#     return box(

#         0,
#         0,
#         width,
#         height
#     )

# # =============================================================================
# # SETBACK POLYGON
# # =============================================================================

# def generate_setback_polygon(

#     plot_polygon: Polygon,

#     front: float = DEFAULT_FRONT_SETBACK,

#     side: float = DEFAULT_SIDE_SETBACK,

#     rear: float = DEFAULT_REAR_SETBACK,

#     facing: str = "north"
# ):

#     minx, miny, maxx, maxy = (
#         plot_polygon.bounds
#     )

#     facing = facing.lower()

#     # -------------------------------------------------------------------------
#     # NORTH
#     # -------------------------------------------------------------------------

#     if facing == "north":

#         poly = box(

#             minx + side,

#             miny + rear,

#             maxx - side,

#             maxy - front
#         )

#     # -------------------------------------------------------------------------
#     # SOUTH
#     # -------------------------------------------------------------------------

#     elif facing == "south":

#         poly = box(

#             minx + side,

#             miny + front,

#             maxx - side,

#             maxy - rear
#         )

#     # -------------------------------------------------------------------------
#     # EAST
#     # -------------------------------------------------------------------------

#     elif facing == "east":

#         poly = box(

#             minx + rear,

#             miny + side,

#             maxx - front,

#             maxy - side
#         )

#     # -------------------------------------------------------------------------
#     # WEST
#     # -------------------------------------------------------------------------

#     else:

#         poly = box(

#             minx + front,

#             miny + side,

#             maxx - rear,

#             maxy - side
#         )

#     return cleanup_geometry(
#         poly
#     )

# # =============================================================================
# # BUILDABLE CORE
# # =============================================================================

# def generate_buildable_core(

#     plot_polygon: Polygon,

#     frontage_polygons: Optional[List[Polygon]] = None,

#     environmental_polygons: Optional[List[Polygon]] = None,

#     front_setback: float = DEFAULT_FRONT_SETBACK,

#     side_setback: float = DEFAULT_SIDE_SETBACK,

#     rear_setback: float = DEFAULT_REAR_SETBACK,

#     facing: str = "north"
# ):

#     frontage_polygons = frontage_polygons or []

#     environmental_polygons = environmental_polygons or []

#     # =========================================================================
#     # STEP 1 — STATUTORY SETBACK CORE
#     # =========================================================================

#     buildable = generate_setback_polygon(

#         plot_polygon=plot_polygon,

#         front=front_setback,

#         side=side_setback,

#         rear=rear_setback,

#         facing=facing
#     )

#     if buildable is None:
#         return None

#     if buildable.is_empty:
#         return None

#     # =========================================================================
#     # STEP 2 — SORT ENVIRONMENTAL SUBTRACTIONS
#     # =========================================================================
#     #
#     # CRITICAL ORDER:
#     #
#     # 1. green strip
#     # 2. walkway setback
#     # 3. backyard
#     # 4. frontage
#     #
#     # =========================================================================

#     green_strip_polys = []
#     walkway_polys = []
#     backyard_polys = []
#     other_env_polys = []

#     for poly in environmental_polygons:

#         if poly is None:
#             continue

#         if poly.is_empty:
#             continue

#         poly = poly.buffer(0)

#         bounds = poly.bounds

#         width = bounds[2] - bounds[0]
#         height = bounds[3] - bounds[1]

#         # ---------------------------------------------------------------------
#         # GREEN STRIP
#         # thin long strip
#         # ---------------------------------------------------------------------

#         if width <= 3.5 or height <= 3.5:

#             green_strip_polys.append(poly)

#         # ---------------------------------------------------------------------
#         # WALKWAY
#         # medium thin strip
#         # ---------------------------------------------------------------------

#         elif width <= 5.0 or height <= 5.0:

#             walkway_polys.append(poly)

#         # ---------------------------------------------------------------------
#         # BACKYARD
#         # larger rear topology
#         # ---------------------------------------------------------------------

#         else:

#             backyard_polys.append(poly)

#     # =========================================================================
#     # STEP 3 — ORDERED SUBTRACTION
#     # =========================================================================

#     subtraction_geometries = []

#     # -------------------------------------------------------------------------
#     # GREEN STRIP FIRST
#     # -------------------------------------------------------------------------

#     subtraction_geometries.extend(
#         green_strip_polys
#     )

#     # -------------------------------------------------------------------------
#     # WALKWAY SECOND
#     # -------------------------------------------------------------------------

#     subtraction_geometries.extend(
#         walkway_polys
#     )

#     # -------------------------------------------------------------------------
#     # BACKYARD THIRD
#     # -------------------------------------------------------------------------

#     subtraction_geometries.extend(
#         backyard_polys
#     )

#     # -------------------------------------------------------------------------
#     # FRONTAGE LAST
#     # -------------------------------------------------------------------------

#     for poly in frontage_polygons:

#         if poly is None:
#             continue

#         if poly.is_empty:
#             continue

#         subtraction_geometries.append(
#             poly.buffer(0)
#         )

#     # =========================================================================
#     # STEP 4 — SAFE UNION + SUBTRACTION
#     # =========================================================================

#     if subtraction_geometries:

#         try:

#             exterior_union = unary_union(
#                 subtraction_geometries
#             )

#             exterior_union = cleanup_geometry(
#                 exterior_union
#             )

#             buildable = buildable.difference(
#                 exterior_union
#             )

#         except Exception as e:

#             print(
#                 f"[BOUNDARY SUBTRACTION ERROR] {e}"
#             )

#     # =========================================================================
#     # STEP 5 — CLEANUP
#     # =========================================================================

#     buildable = cleanup_geometry(
#         buildable
#     )

#     buildable = remove_small_fragments(
#         buildable
#     )

#     buildable = cleanup_geometry(
#         buildable
#     )

#     # =========================================================================
#     # STEP 6 — VALIDATION
#     # =========================================================================

#     if buildable is None:
#         return None

#     if buildable.is_empty:
#         return None

#     if buildable.area < MIN_BUILDABLE_AREA:
#         return None

#     return buildable

# # =============================================================================
# # REMOVE SMALL FRAGMENTS
# # =============================================================================

# def remove_small_fragments(geometry):

#     if geometry is None:
#         return Polygon()

#     if geometry.is_empty:
#         return Polygon()

#     # -------------------------------------------------------------------------
#     # MULTIPOLYGON
#     # -------------------------------------------------------------------------

#     if isinstance(

#         geometry,

#         MultiPolygon
#     ):

#         valid_parts = []

#         for poly in geometry.geoms:

#             if poly.area >= MIN_FRAGMENT_AREA:

#                 valid_parts.append(
#                     poly
#                 )

#         if not valid_parts:

#             return Polygon()

#         geometry = max(

#             valid_parts,

#             key=lambda x: x.area
#         )

#     # -------------------------------------------------------------------------
#     # SINGLE
#     # -------------------------------------------------------------------------

#     if geometry.area < MIN_FRAGMENT_AREA:

#         return Polygon()

#     return geometry.buffer(0)

# # =============================================================================
# # CLEAN GEOMETRY
# # =============================================================================

# def cleanup_geometry(geometry):

#     if geometry is None:

#         return Polygon()

#     if geometry.is_empty:

#         return Polygon()

#     try:

#         geometry = geometry.buffer(
#             GEOMETRY_BUFFER
#         )

#         geometry = geometry.buffer(
#             -GEOMETRY_BUFFER
#         )

#         geometry = geometry.buffer(0)

#     except Exception:

#         return Polygon()

#     if geometry.is_empty:

#         return Polygon()

#     return geometry

# # =============================================================================
# # DEBUG
# # =============================================================================

# def boundary_debug(

#     plot_polygon,

#     buildable_polygon
# ):

#     print("\n" + "=" * 60)
#     print("BOUNDARY MANAGER")
#     print("=" * 60)

#     print(
#         f"Plot Area       : "
#         f"{plot_polygon.area:.1f}"
#     )

#     if buildable_polygon is not None:

#         print(
#             f"Buildable Area  : "
#             f"{buildable_polygon.area:.1f}"
#         )

#         ratio = (

#             buildable_polygon.area
#             /
#             plot_polygon.area
#         ) * 100

#         print(
#             f"Efficiency      : "
#             f"{ratio:.1f}%"
#         )

#     else:

#         print(
#             "Buildable Area  : INVALID"
#         )

# # =============================================================================
# # EXPORTS
# # =============================================================================

# __all__ = [

#     "create_plot_boundary",

#     "generate_setback_polygon",

#     "generate_buildable_core",

#     "cleanup_geometry",

#     "remove_small_fragments",

#     "boundary_debug"
# ]




# =============================================================================
# boundary_manager.py
# ARCHIVERSE — DYNAMIC BUILDABLE ENGINE v14
# =============================================================================

from typing import List
from typing import Optional

from shapely.geometry import (
    Polygon,
    MultiPolygon,
    box
)

from shapely.ops import unary_union

# =============================================================================
# CONSTANTS
# =============================================================================

MIN_BUILDABLE_AREA = 220.0
MIN_FRAGMENT_AREA = 120.0

GEOMETRY_BUFFER = 0.01

DEFAULT_FRONT_SETBACK = 4.0
DEFAULT_SIDE_SETBACK  = 3.0
DEFAULT_REAR_SETBACK  = 5.0

# =============================================================================
# PLOT
# =============================================================================

def create_plot_boundary(
    width: float,
    height: float
) -> Polygon:

    return box(
        0,
        0,
        width,
        height
    )

# =============================================================================
# DYNAMIC SETBACK ENGINE
# =============================================================================

def dynamic_setbacks(
    width,
    height,
    facing
):

    area = width * height

    front = DEFAULT_FRONT_SETBACK
    side  = DEFAULT_SIDE_SETBACK
    rear  = DEFAULT_REAR_SETBACK

    # =====================================================================
    # SMALL PLOTS
    # =====================================================================

    if area <= 1500:

        front = 3.5
        side  = 2.5
        rear  = 4.0

    # =====================================================================
    # MEDIUM
    # =====================================================================

    elif area <= 2400:

        front = 4.0
        side  = 3.0
        rear  = 5.0

    # =====================================================================
    # LARGE
    # =====================================================================

    else:

        front = 5.0
        side  = 4.0
        rear  = 6.0

    # =====================================================================
    # FACING MODIFIERS
    # =====================================================================

    facing = facing.lower()

    # ---------------------------------------------------------------------
    # EAST
    # more west usable
    # ---------------------------------------------------------------------

    if facing == "east":

        rear += 1.0

    # ---------------------------------------------------------------------
    # WEST
    # keep SW bigger
    # ---------------------------------------------------------------------

    elif facing == "west":

        side = max(2.5, side - 0.5)

    # ---------------------------------------------------------------------
    # SOUTH
    # bigger north buildable
    # ---------------------------------------------------------------------

    elif facing == "south":

        rear += 1.0

    return {

        "front": front,
        "side": side,
        "rear": rear
    }

# =============================================================================
# SETBACK POLYGON
# =============================================================================

def generate_setback_polygon(

    plot_polygon: Polygon,

    front: float,

    side: float,

    rear: float,

    facing: str
):

    minx, miny, maxx, maxy = (
        plot_polygon.bounds
    )

    facing = facing.lower()

    # =====================================================================
    # NORTH
    # =====================================================================

    if facing == "north":

        poly = box(

            minx + side,
            miny + rear,

            maxx - side,
            maxy - front
        )

    # =====================================================================
    # SOUTH
    # =====================================================================

    elif facing == "south":

        poly = box(

            minx + side,
            miny + front,

            maxx - side,
            maxy - rear
        )

    # =====================================================================
    # EAST
    # =====================================================================

    elif facing == "east":

        poly = box(

            minx + rear,
            miny + side,

            maxx - front,
            maxy - side
        )

    # =====================================================================
    # WEST
    # =====================================================================

    else:

        poly = box(

            minx + front,
            miny + side,

            maxx - rear,
            maxy - side
        )

    return cleanup_geometry(poly)

# =============================================================================
# BUILDABLE CORE
# =============================================================================

def generate_buildable_core(

    plot_polygon: Polygon,

    frontage_polygons: Optional[List[Polygon]] = None,

    environmental_polygons: Optional[List[Polygon]] = None,

    front_setback: float = None,

    side_setback: float = None,

    rear_setback: float = None,

    facing: str = "north"
):

    frontage_polygons = frontage_polygons or []
    environmental_polygons = environmental_polygons or []

    # =====================================================================
    # DYNAMIC SETBACKS
    # =====================================================================

    minx, miny, maxx, maxy = (
        plot_polygon.bounds
    )

    width  = maxx - minx
    height = maxy - miny

    dynamic = dynamic_setbacks(

        width,
        height,
        facing
    )

    front_setback = (
        front_setback
        if front_setback is not None
        else dynamic["front"]
    )

    side_setback = (
        side_setback
        if side_setback is not None
        else dynamic["side"]
    )

    rear_setback = (
        rear_setback
        if rear_setback is not None
        else dynamic["rear"]
    )

    # =====================================================================
    # BUILDABLE
    # =====================================================================

    buildable = generate_setback_polygon(

        plot_polygon=plot_polygon,

        front=front_setback,
        side=side_setback,
        rear=rear_setback,

        facing=facing
    )

    if buildable is None:
        return None

    if buildable.is_empty:
        return None

    # =====================================================================
    # ENVIRONMENT SORTING
    # =====================================================================

    green_strip_polys = []
    walkway_polys = []
    backyard_polys = []
    misc_polys = []

    for poly in environmental_polygons:

        if poly is None:
            continue

        if poly.is_empty:
            continue

        poly = cleanup_geometry(poly)

        bx0, by0, bx1, by1 = (
            poly.bounds
        )

        w = bx1 - bx0
        h = by1 - by0

        # -----------------------------------------------------------------
        # GREEN STRIP
        # -----------------------------------------------------------------

        if w <= 3.5 or h <= 3.5:

            green_strip_polys.append(poly)

        # -----------------------------------------------------------------
        # WALKWAY
        # -----------------------------------------------------------------

        elif w <= 5.0 or h <= 5.0:

            walkway_polys.append(poly)

        # -----------------------------------------------------------------
        # BACKYARD
        # -----------------------------------------------------------------

        elif poly.area >= 80:

            backyard_polys.append(poly)

        else:

            misc_polys.append(poly)

    # =====================================================================
    # SUBTRACTION ORDER
    # =====================================================================

    subtraction_geometries = []

    subtraction_geometries.extend(
        green_strip_polys
    )

    subtraction_geometries.extend(
        walkway_polys
    )

    subtraction_geometries.extend(
        backyard_polys
    )

    subtraction_geometries.extend(
        misc_polys
    )

    subtraction_geometries.extend(
        frontage_polygons
    )

    # =====================================================================
    # SAFE DIFFERENCE
    # =====================================================================

    if subtraction_geometries:

        try:

            subtract_union = unary_union(
                subtraction_geometries
            )

            subtract_union = cleanup_geometry(
                subtract_union
            )

            buildable = buildable.difference(
                subtract_union
            )

        except Exception as e:

            print(
                f"[BOUNDARY ERROR] {e}"
            )

    # =====================================================================
    # CLEANUP
    # =====================================================================

    buildable = cleanup_geometry(
        buildable
    )

    buildable = remove_small_fragments(
        buildable
    )

    buildable = cleanup_geometry(
        buildable
    )

    # =====================================================================
    # VALIDATION
    # =====================================================================

    if buildable is None:
        return None

    if buildable.is_empty:
        return None

    if buildable.area < MIN_BUILDABLE_AREA:
        return None

    return buildable

# =============================================================================
# REMOVE SMALL FRAGMENTS
# =============================================================================

def remove_small_fragments(geometry):

    if geometry is None:
        return Polygon()

    if geometry.is_empty:
        return Polygon()

    # =====================================================================
    # MULTI
    # =====================================================================

    if isinstance(
        geometry,
        MultiPolygon
    ):

        valid = []

        for poly in geometry.geoms:

            if poly.area >= MIN_FRAGMENT_AREA:

                valid.append(poly)

        if not valid:
            return Polygon()

        geometry = max(
            valid,
            key=lambda x: x.area
        )

    # =====================================================================
    # SINGLE
    # =====================================================================

    if geometry.area < MIN_FRAGMENT_AREA:

        return Polygon()

    return geometry.buffer(0)

# =============================================================================
# CLEANUP
# =============================================================================

def cleanup_geometry(geometry):

    if geometry is None:
        return Polygon()

    if geometry.is_empty:
        return Polygon()

    try:

        geometry = geometry.buffer(
            GEOMETRY_BUFFER
        )

        geometry = geometry.buffer(
            -GEOMETRY_BUFFER
        )

        geometry = geometry.buffer(0)

    except Exception:

        return Polygon()

    if geometry.is_empty:
        return Polygon()

    return geometry

# =============================================================================
# DEBUG
# =============================================================================

def boundary_debug(

    plot_polygon,
    buildable_polygon
):

    print("\n" + "=" * 60)
    print("BOUNDARY MANAGER")
    print("=" * 60)

    print(
        f"Plot Area       : "
        f"{plot_polygon.area:.1f}"
    )

    if buildable_polygon is not None:

        print(
            f"Buildable Area  : "
            f"{buildable_polygon.area:.1f}"
        )

        efficiency = (

            buildable_polygon.area
            /
            plot_polygon.area
        ) * 100

        print(
            f"Efficiency      : "
            f"{efficiency:.1f}%"
        )

    else:

        print(
            "Buildable Area  : INVALID"
        )

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [

    "create_plot_boundary",

    "generate_setback_polygon",

    "generate_buildable_core",

    "cleanup_geometry",

    "remove_small_fragments",

    "boundary_debug",

    "dynamic_setbacks"
]