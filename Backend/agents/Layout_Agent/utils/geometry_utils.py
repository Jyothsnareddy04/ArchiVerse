# =============================================================================
# GEOMETRY UTILITIES v6
# =============================================================================
# Topology-safe geometry helper functions
#
# RESPONSIBILITIES
#
# - polygon metrics
# - adjacency
# - residual carving
# - topology-safe cleanup
# - spatial relationships
#
# DOES NOT:
#
# - reshape topology
# - force rectangles
# - orthogonalize rooms
# - mutate architecture
# =============================================================================

from typing import List
from typing import Optional
from typing import Tuple

from shapely.geometry import (
    Polygon,
    MultiPolygon,
    GeometryCollection,
    box
)

from shapely.ops import unary_union

# =============================================================================
# SAFE CLEAN
# =============================================================================

def safe_clean(

    poly
):

    if poly is None:

        return None

    if poly.is_empty:

        return None

    try:

        poly = poly.buffer(
            0.05
        ).buffer(
            -0.05
        )

    except:

        return None

    if poly.is_empty:

        return None

    if not poly.is_valid:

        return None

    return poly

# =============================================================================
# RECTANGLE
# =============================================================================

def rect_from_bounds(

    x: float,

    y: float,

    w: float,

    h: float
) -> Polygon:

    return box(

        x,
        y,

        x + w,
        y + h
    )

# =============================================================================
# CLAMP
# =============================================================================

def clamp(

    value: float,

    lo: float,

    hi: float
):

    return max(

        lo,

        min(
            hi,
            value
        )
    )

# =============================================================================
# DIMENSIONS
# =============================================================================

def polygon_dimensions(

    poly: Polygon
):

    if poly is None:

        return (0, 0)

    minx, miny, maxx, maxy = poly.bounds

    return (

        maxx - minx,

        maxy - miny
    )

# =============================================================================
# ASPECT RATIO
# =============================================================================

def aspect_ratio(

    poly: Polygon
):

    if poly is None:

        return 999

    w, h = polygon_dimensions(
        poly
    )

    if h <= 0 or w <= 0:

        return 999

    return max(

        w,
        h

    ) / max(

        min(w, h),
        1
    )

# =============================================================================
# COMPACTNESS
# =============================================================================

def compactness(

    poly
):

    if poly is None:

        return 0.0

    if poly.area <= 0:

        return 0.0

    if poly.length <= 0:

        return 0.0

    return (

        4 * 3.14159 * poly.area

    ) / (

        poly.length ** 2
    )

# =============================================================================
# CENTER
# =============================================================================

def polygon_center(

    poly: Polygon
):

    if poly is None:

        return (0, 0)

    c = poly.centroid

    return (

        c.x,
        c.y
    )

# =============================================================================
# DISTANCE
# =============================================================================

def distance_between_spaces(

    a: Polygon,

    b: Polygon
):

    if a is None or b is None:

        return 999

    return a.distance(b)

# =============================================================================
# ADJACENT
# =============================================================================

def are_adjacent(

    a: Polygon,

    b: Polygon,

    tolerance: float = 1.0
):

    if a is None or b is None:

        return False

    shared = (

        a.buffer(0.3).boundary.intersection(

            b.buffer(0.3).boundary
        )
    )

    if shared.length >= tolerance:

        return True

    overlap = a.buffer(1).intersection(

        b.buffer(1)
    )

    return overlap.area > 2

# =============================================================================
# EXTERIOR TOUCH
# =============================================================================

def touches_exterior(

    poly: Polygon,

    boundary: Polygon,

    min_touch=1
):

    if poly is None:

        return False

    shared = (

        poly.buffer(0.3).boundary.intersection(

            boundary.boundary
        )
    )

    return shared.length >= min_touch

# =============================================================================
# RESIDUAL
# =============================================================================

def subtract_polygons(

    base: Polygon,

    cuts: List[Polygon]
):

    if base is None:

        return None

    if len(cuts) == 0:

        return base

    valid = []

    for c in cuts:

        if c is None:
            continue

        if c.is_empty:
            continue

        valid.append(c)

    if len(valid) == 0:

        return base

    merged = unary_union(valid)

    try:

        result = base.difference(
            merged
        )

    except:

        return base

    return safe_clean(result)

# =============================================================================
# LARGEST REGION
# =============================================================================

def largest_polygon(

    geometry
):

    if geometry is None:

        return None

    if geometry.is_empty:

        return None

    if isinstance(
        geometry,
        Polygon
    ):

        return geometry

    if isinstance(
        geometry,
        MultiPolygon
    ):

        polys = [

            p for p in geometry.geoms

            if p.area > 20
        ]

        if len(polys) == 0:

            return None

        polys.sort(

            key=lambda p: p.area,

            reverse=True
        )

        return polys[0]

    return None

# =============================================================================
# FIT RECTANGLE
# =============================================================================

def fit_rectangle_in_remaining(

    remaining: Polygon,

    width: float,

    height: float,

    anchor: str = "south-west"
):

    if remaining is None:

        return None

    if remaining.is_empty:

        return None

    poly = largest_polygon(
        remaining
    )

    if poly is None:

        return None

    minx, miny, maxx, maxy = (
        poly.bounds
    )

    pw = maxx - minx
    ph = maxy - miny

    w = min(width, pw)
    h = min(height, ph)

    if w < width * 0.72:

        return None

    if h < height * 0.72:

        return None

    anchor = anchor.lower()

    if anchor == "south-west":

        x = minx
        y = miny

    elif anchor == "south-east":

        x = maxx - w
        y = miny

    elif anchor == "north-west":

        x = minx
        y = maxy - h

    elif anchor == "north-east":

        x = maxx - w
        y = maxy - h

    else:

        x = minx + (pw - w) / 2
        y = miny + (ph - h) / 2

    rect = rect_from_bounds(

        x,
        y,

        w,
        h
    )

    rect = rect.intersection(
        poly
    )

    rect = safe_clean(rect)

    if rect is None:

        return None

    if rect.area < (

        width
        * height
        * 0.55
    ):

        return None

    return rect

# =============================================================================
# SHARED WALL
# =============================================================================

def shared_wall_length(

    a,

    b
):

    if a is None or b is None:

        return 0.0

    inter = a.buffer(0.2).boundary.intersection(

        b.buffer(0.2).boundary
    )

    return inter.length

# =============================================================================
# POLYGON SCORE
# =============================================================================

def polygon_quality_score(

    poly: Polygon
):

    if poly is None:

        return 0.0

    ratio = aspect_ratio(
        poly
    )

    comp = compactness(
        poly
    )

    score = 100

    # =============================================================
    # ASPECT
    # =============================================================

    if ratio > 6:

        score -= 25

    elif ratio > 4:

        score -= 15

    elif ratio > 3:

        score -= 5

    # =============================================================
    # COMPACTNESS
    # =============================================================

    if comp < 0.12:

        score -= 25

    elif comp < 0.20:

        score -= 12

    elif comp < 0.30:

        score -= 5

    return max(score, 0)

# =============================================================================
# DEAD SPACE
# =============================================================================

def detect_dead_space(

    residual,

    min_area=25
):

    regions = []

    if residual is None:

        return regions

    if residual.is_empty:

        return regions

    if isinstance(
        residual,
        Polygon
    ):

        polys = [residual]

    elif isinstance(
        residual,
        MultiPolygon
    ):

        polys = list(
            residual.geoms
        )

    else:

        return regions

    for poly in polys:

        if poly.area < min_area:

            continue

        regions.append({

            "polygon":
            poly,

            "area":
            poly.area,

            "aspect_ratio":
            aspect_ratio(poly),

            "compactness":
            compactness(poly)
        })

    return regions

# =============================================================================
# VENTILATION
# =============================================================================

def ventilation_score(

    poly: Polygon,

    buildable: Polygon
):

    if poly is None:

        return 0

    shared = (

        poly.buffer(0.3).boundary.intersection(

            buildable.boundary
        )
    )

    return shared.length

# =============================================================================
# ALIGNMENT
# =============================================================================

def aligned(

    a: Polygon,

    b: Polygon,

    tolerance=2.0
):

    if a is None or b is None:

        return False

    ac = polygon_center(a)

    bc = polygon_center(b)

    return (

        abs(ac[0] - bc[0]) <= tolerance

        or

        abs(ac[1] - bc[1]) <= tolerance
    )

# =============================================================================
# CONNECTIVITY GRAPH
# =============================================================================

def connectivity_graph(

    polygons: List[Polygon]
):

    graph = {}

    for i in range(len(polygons)):

        graph[i] = []

        for j in range(len(polygons)):

            if i == j:

                continue

            if are_adjacent(

                polygons[i],

                polygons[j]
            ):

                graph[i].append(j)

    return graph