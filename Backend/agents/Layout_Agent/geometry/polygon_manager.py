# =============================================================================
# TOPOLOGY-AWARE POLYGON MANAGER
# =============================================================================
# Production geometry utilities for ArchiVerse
#
# IMPORTANT:
# This engine preserves:
# - MultiPolygon topology
# - residual regions
# - circulation pockets
# - environmental openings
#
# NEVER collapse geometry to:
# largest rectangle
# =============================================================================

from typing import (
    Optional,
    Tuple,
    List,
    Dict
)

from shapely.geometry import (
    Polygon,
    MultiPolygon,
    box,
    Point
)

from shapely.ops import (
    unary_union
)

from shapely import affinity

from config.constants import *

# =============================================================================
# RECTANGLE
# =============================================================================


def create_rectangle(

    x: float,

    y: float,

    width: float,

    height: float

) -> Polygon:

    return box(
        x,
        y,
        x + width,
        y + height
    )

# =============================================================================
# BOUNDS
# =============================================================================


def get_bounds(

    poly: Polygon

) -> Tuple[float, float, float, float]:

    return poly.bounds

# =============================================================================
# DIMENSIONS
# =============================================================================


def get_dimensions(

    poly: Polygon

) -> Tuple[float, float]:

    minx, miny, maxx, maxy = poly.bounds

    return (
        maxx - minx,
        maxy - miny
    )

# =============================================================================
# CONTAINMENT
# =============================================================================


def polygon_contains(

    outer: Polygon,

    inner: Polygon,

    tolerance: float = 0.25

) -> bool:

    return outer.buffer(
        tolerance
    ).contains(inner)

# =============================================================================
# OVERLAP
# =============================================================================


def polygon_overlap_area(

    a: Polygon,

    b: Polygon

) -> float:

    if not a.intersects(b):

        return 0.0

    return a.intersection(
        b
    ).area

# =============================================================================
# MULTIPOLYGON SAFE SUBTRACTION
# =============================================================================


def subtract_polygon(

    base,

    cut

) -> List[Polygon]:

    """
    IMPORTANT:
    NEVER collapse to largest polygon.

    Preserve all topology regions.
    """

    if base is None:

        return []

    if base.is_empty:

        return []

    result = base.difference(
        cut
    )

    if result.is_empty:

        return []

    # =====================================================
    # MULTIPOLYGON
    # =====================================================

    if isinstance(
        result,
        MultiPolygon
    ):

        return [

            p for p in result.geoms

            if p.area >= MIN_REGION_AREA
        ]

    # =====================================================
    # SINGLE POLYGON
    # =====================================================

    if result.area < MIN_REGION_AREA:

        return []

    return [result]

# =============================================================================
# RESIDUAL REGION ANALYSIS
# =============================================================================


def analyze_region(

    polygon: Polygon

) -> Dict:

    bounds = polygon.bounds

    width = bounds[2] - bounds[0]

    height = bounds[3] - bounds[1]

    aspect_ratio = max(
        width,
        height
    ) / max(
        min(width, height),
        1
    )

    perimeter = polygon.length

    compactness = 0

    if perimeter > 0:

        compactness = (

            4
            * 3.14159
            * polygon.area

        ) / (

            perimeter ** 2
        )

    return {

        "polygon": polygon,

        "area": polygon.area,

        "width": width,

        "height": height,

        "aspect_ratio": aspect_ratio,

        "compactness": compactness,

        "center": polygon.centroid
    }

# =============================================================================
# FILTER VALID REGIONS
# =============================================================================


def filter_valid_regions(

    polygons: List[Polygon]

) -> List[Polygon]:

    valid = []

    for poly in polygons:

        if poly.area < MIN_REGION_AREA:

            continue

        bounds = poly.bounds

        w = bounds[2] - bounds[0]

        h = bounds[3] - bounds[1]

        ratio = max(w, h) / max(
            min(w, h),
            1
        )

        if ratio > (
            MAX_REGION_ASPECT_RATIO * 1.5
        ):

            valid.append(poly)

    return valid

# =============================================================================
# LARGEST RECTANGLE APPROXIMATION
# =============================================================================

def largest_rectangle_in_polygon(

    poly: Polygon

):

    return poly

# =============================================================================
# MIRROR
# =============================================================================


def mirror_polygon_x(

    poly: Polygon,

    axis_x: float

):

    return affinity.scale(

        poly,

        xfact=-1,

        origin=(axis_x, 0, 0)
    )

# =============================================================================
# SNAP TO EDGE
# =============================================================================


def snap_to_edge(

    buildable: Polygon,

    width: float,

    height: float,

    edge: str,

    offset: float = 0.0

) -> Polygon:

    bx0, by0, bx1, by1 = (
        buildable.bounds
    )

    bw = bx1 - bx0

    bh = by1 - by0

    width = min(width, bw)

    height = min(height, bh)

    edge = edge.lower().strip()

    # =====================================================
    # CORNERS
    # =====================================================

    if edge == "south-west":

        x = bx0 + offset

        y = by0 + offset

    elif edge == "south-east":

        x = bx1 - width - offset

        y = by0 + offset

    elif edge == "north-west":

        x = bx0 + offset

        y = by1 - height - offset

    elif edge == "north-east":

        x = bx1 - width - offset

        y = by1 - height - offset

    # =====================================================
    # EDGES
    # =====================================================

    elif edge == "south":

        x = bx0 + offset

        y = by0

    elif edge == "north":

        x = bx0 + offset

        y = by1 - height

    elif edge == "west":

        x = bx0

        y = by0 + offset

    elif edge == "east":

        x = bx1 - width

        y = by0 + offset

    else:

        x = bx0

        y = by0

    return box(
        x,
        y,
        x + width,
        y + height
    )

# =============================================================================
# TOUCHES EXTERIOR
# =============================================================================


def touches_exterior(

    polygon: Polygon,

    boundary: Polygon,

    min_touch: float = MIN_EXTERIOR_TOUCH

) -> bool:

    shared = polygon.boundary.intersection(
        boundary.boundary
    )

    return shared.length >= (
        min_touch * 0.5
    )

# =============================================================================
# SHARED EDGE LENGTH
# =============================================================================


def shared_edge_length(

    a: Polygon,

    b: Polygon

) -> float:

    shared = a.boundary.intersection(
        b.boundary
    )

    return shared.length

# =============================================================================
# CONNECTIVITY GRAPH
# =============================================================================


def build_connectivity_graph(

    polygons: Dict[str, Polygon]

):

    graph = {}

    keys = list(polygons.keys())

    for k in keys:

        graph[k] = []

    for i in range(len(keys)):

        for j in range(i + 1, len(keys)):

            a = polygons[keys[i]]

            b = polygons[keys[j]]

            shared = shared_edge_length(
                a,
                b
            )

            if shared >= 2.0:

                graph[keys[i]].append(
                    keys[j]
                )

                graph[keys[j]].append(
                    keys[i]
                )

    return graph

# =============================================================================
# REGION SCORING
# =============================================================================


def score_region(

    polygon: Polygon,

    buildable: Polygon,

    prefer_exterior: bool = False,

    prefer_private: bool = False

):

    analysis = analyze_region(
        polygon
    )

    score = 0.0

    # =====================================================
    # AREA
    # =====================================================

    score += min(
        analysis["area"] / 100,
        15
    )

    # =====================================================
    # COMPACTNESS
    # =====================================================

    score += (
        analysis["compactness"]
        * 40
    )

    # =====================================================
    # ASPECT
    # =====================================================

    score += max(

        0,

        10
        -
        analysis["aspect_ratio"]
    )

    # =====================================================
    # EXTERIOR
    # =====================================================

    if prefer_exterior:

        if touches_exterior(
            polygon,
            buildable
        ):

            score += 20

    # =====================================================
    # PRIVACY
    # =====================================================

    if prefer_private:

        centroid = polygon.centroid

        bx0, by0, bx1, by1 = (
            buildable.bounds
        )

        cx = (bx0 + bx1) / 2

        cy = (by0 + by1) / 2

        dist = Point(
            cx,
            cy
        ).distance(centroid)

        score += dist

    return round(score, 2)

# =============================================================================
# UNION
# =============================================================================


def merge_polygons(

    polygons: List[Polygon]

):

    return unary_union(polygons)