# =============================================================================
# TOPOLOGY-AWARE WALL GENERATOR v12
# =============================================================================
# Layout-Agent Level Wall Skeleton Generator
#
# RESPONSIBILITIES
#
# - room boundary walls
# - exterior walls
# - interior walls
# - wet wall detection
# - circulation graph edges
# - main entry alignment
# - structural wall candidates
# - wall connectivity graph
#
# IMPORTANT
#
# NO:
# - windows
# - room doors
# - door swings
# - wall offsets
# - BIM elements
# - detailed drafting
#
# Those belong to:
# Blueprint Agent
# =============================================================================

from typing import (
    List,
    Dict
)

from shapely.geometry import (
    Polygon,
    LineString,
    MultiLineString,
    Point
)

from shapely.ops import unary_union

from state import Space

from config.constants import (
    OUTER_WALL,
    INNER_WALL
)

# =============================================================================
# MAIN ENGINE
# =============================================================================

def generate_walls(

    spaces: List[Space],

    buildable: Polygon,

    facing="north"
):

    walls = {

        "exterior": [],

        "interior": [],

        "wet_walls": [],

        "connectivity_graph": {},

        "main_entry": None
    }

    # =====================================================
    # EXTERIOR
    # =====================================================

    walls["exterior"] = _generate_exterior_walls(
        buildable
    )

    # =====================================================
    # INTERIOR
    # =====================================================

    interior, wet = _generate_interior_walls(
        spaces
    )

    walls["interior"] = interior

    walls["wet_walls"] = wet

    # =====================================================
    # WALL GRAPH
    # =====================================================

    walls["connectivity_graph"] = _generate_wall_graph(
        spaces
    )

    # =====================================================
    # MAIN ENTRY
    # =====================================================

    walls["main_entry"] = _generate_main_entry(

        spaces,
        buildable,
        facing
    )

    # =====================================================
    # REPORT
    # =====================================================

    print(

        f"\n[WALL ENGINE]"

        f"\n  exterior        : {len(walls['exterior'])}"

        f"\n  interior        : {len(walls['interior'])}"

        f"\n  wet walls       : {len(walls['wet_walls'])}"
    )

    return walls

# =============================================================================
# EXTERIOR WALLS
# =============================================================================

def _generate_exterior_walls(

    buildable: Polygon
):

    walls = []

    coords = list(
        buildable.exterior.coords
    )

    for i in range(len(coords) - 1):

        seg = LineString([

            coords[i],
            coords[i + 1]
        ])

        structural = seg.length >= 12

        walls.append({

            "line": seg,

            "type":

                "structural_exterior"

                if structural

                else

                "partition_exterior",

            "thickness": OUTER_WALL,

            "load_bearing": structural
        })

    return walls

# =============================================================================
# INTERIOR WALLS
# =============================================================================

def _generate_interior_walls(

    spaces: List[Space]
):

    interior = []

    wet_walls = []

    for i in range(len(spaces)):

        for j in range(i + 1, len(spaces)):

            a = spaces[i]
            b = spaces[j]
            
            environmental = [

                "green_strip",
                "green_buffer",
                "parking",
                "lawn",
                "backyard",
                "main_gate"
            ]

            if a.room_type in environmental:
                continue

            if b.room_type in environmental:
                continue

            shared = a.polygon.boundary.intersection(
                b.polygon.boundary
            )

            # =========================================================
            # INVALID
            # =========================================================

            if shared.is_empty:
                continue

            if shared.length < 2.5:
                continue

            if hasattr(shared, "geoms"):

                valid = []

                for g in shared.geoms:

                    if g.length < 1:
                        continue

                    valid.append(g)

                if len(valid) == 0:
                    continue

                shared = unary_union(valid)

            shared = shared.simplify(
                0.01
            )

            # =========================================================
            # ROOM TYPES
            # =========================================================

            wet_keywords = [

                "kitchen",
                "bathroom",
                "wash_area"
            ]

            a_wet = any(
                x in a.name
                for x in wet_keywords
            )

            b_wet = any(
                x in b.name
                for x in wet_keywords
            )

            is_wet = a_wet or b_wet

            # =========================================================
            # THICKNESS
            # =============================================================

            thickness = INNER_WALL

            if is_wet:

                thickness *= 1.25

            wall = {

                "line": shared,

                "rooms": (
                    a.name,
                    b.name
                ),

                "thickness": thickness,

                "plumbing_core": is_wet,

                "type":

                    "wet_wall"

                    if is_wet

                    else

                    "interior"

            }

            if is_wet:

                wet_walls.append(
                    wall
                )

            else:

                interior.append(
                    wall
                )

    return interior, wet_walls

# =============================================================================
# WALL CONNECTIVITY GRAPH
# =============================================================================

def _generate_wall_graph(

    spaces: List[Space]
):

    graph = {}

    for s in spaces:

        graph[s.name] = []

    for i in range(len(spaces)):

        for j in range(i + 1, len(spaces)):

            a = spaces[i]
            b = spaces[j]

            shared = a.polygon.boundary.intersection(
                b.polygon.boundary
            )
            
            environmental = [

                "green_strip",
                "green_buffer",
                "parking",
                "lawn",
                "backyard",
                "main_gate"
            ]

            if a.room_type in environmental:
                continue

            if b.room_type in environmental:
                continue

            if shared.is_empty:
                continue

            if shared.length < 1:
                continue

            graph[a.name].append(
                b.name
            )

            graph[b.name].append(
                a.name
            )

    return graph

def _generate_main_entry(

    spaces,

    buildable,

    facing
):

    bx0, by0, bx1, by1 = (
        buildable.bounds
    )

    if facing == "north":

        point = Point(
            (bx0 + bx1) / 2,
            by1
        )

    elif facing == "south":

        point = Point(
            (bx0 + bx1) / 2,
            by0
        )

    elif facing == "east":

        point = Point(
            bx1,
            (by0 + by1) / 2
        )

    else:

        point = Point(
            bx0,
            (by0 + by1) / 2
        )

    return {

        "point": point,

        "type": "main_entry",

        "width": 5.0
    }
    
    
# =============================================================================
# WALL CENTERLINES
# =============================================================================

def extract_wall_centerlines(

    walls: Dict
):

    lines = []

    categories = [

        "exterior",
        "interior",
        "wet_walls"
    ]

    for category in categories:

        for item in walls[category]:

            geom = item["line"]

            if isinstance(
                geom,
                LineString
            ):

                lines.append(geom)

            elif isinstance(
                geom,
                MultiLineString
            ):

                for g in geom.geoms:

                    lines.append(g)

    return lines

# =============================================================================
# WALL STATISTICS
# =============================================================================

def wall_statistics(

    walls: Dict
):

    exterior = sum([

        w["line"].length

        for w in walls["exterior"]
    ])

    interior = sum([

        w["line"].length

        for w in walls["interior"]
    ])

    wet = sum([

        w["line"].length

        for w in walls["wet_walls"]
    ])

    return {

        "exterior_wall_length":
        round(exterior, 2),

        "interior_wall_length":
        round(interior, 2),

        "wet_wall_length":
        round(wet, 2),

        "total_wall_length":
        round(
            exterior + interior + wet,
            2
        )
    }