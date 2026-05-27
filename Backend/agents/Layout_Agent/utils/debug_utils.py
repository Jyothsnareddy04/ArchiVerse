# =============================================================================
# DEBUG UTILITIES v5
# =============================================================================
# Production topology debugging utilities
#
# Handles:
# - topology summary
# - zoning summary
# - circulation analysis
# - environmental diagnostics
# - polygon diagnostics
# - overlap debugging
# =============================================================================

from collections import defaultdict

from shapely.geometry import (
    Polygon,
    MultiPolygon
)

from state import LayoutState

# =============================================================================
# STATE SUMMARY
# =============================================================================


def print_state_summary(

    state: LayoutState
):

    print("\n" + "=" * 80)

    print("ARCHIVERSE TOPOLOGY STATE")

    print("=" * 80)

    # =========================================================================
    # PLOT
    # =========================================================================

    print("\n[PLOT]")

    print(

        f"  Plot Size          : "
        f"{state.plot_width} x {state.plot_height} ft"
    )

    print(

        f"  Plot Area          : "
        f"{state.plot_width * state.plot_height:.1f} sqft"
    )

    print(

        f"  Facing             : "
        f"{state.facing}"
    )

    print(

        f"  Bedrooms           : "
        f"{state.bedrooms}"
    )

    print(

        f"  Bathrooms          : "
        f"{state.bathrooms}"
    )

    print(

        f"  Optional Rooms     : "
        f"{state.optional_rooms}"
    )

    # =========================================================================
    # BUILDABLE
    # =========================================================================

    if state.buildable_polygon:

        bx0, by0, bx1, by1 = (

            state.buildable_polygon.bounds
        )

        print("\n[BUILDABLE]")

        print(

            f"  Bounds             : "
            f"({bx0:.1f}, {by0:.1f})"
            f" → "
            f"({bx1:.1f}, {by1:.1f})"
        )

        print(

            f"  Width              : "
            f"{bx1 - bx0:.1f} ft"
        )

        print(

            f"  Height             : "
            f"{by1 - by0:.1f} ft"
        )

        print(

            f"  Area               : "
            f"{state.buildable_polygon.area:.1f} sqft"
        )

    # =========================================================================
    # TOPOLOGY
    # =========================================================================

    print("\n[TOPOLOGY]")

    print(

        f"  Spaces             : "
        f"{len(state.spaces)}"
    )

    print(

        f"  Placed Area        : "
        f"{state.placed_area:.1f} sqft"
    )

    print(

        f"  Utilisation        : "
        f"{state.utilisation * 100:.1f}%"
    )

    print(

        f"  Score              : "
        f"{state.score}/100"
    )

    # =========================================================================
    # ZONES
    # =========================================================================

    zone_groups = defaultdict(list)

    for s in state.spaces:

        zone_groups[s.zone].append(
            s.name
        )

    print("\n[ZONES]")

    for zone, rooms in zone_groups.items():

        print(

            f"  {zone:15s}"
            f"{len(rooms)} rooms"
        )

        print(
            f"    {rooms}"
        )

    # =========================================================================
    # ROOM TABLE
    # =========================================================================

    print("\n[ROOMS]")

    header = (

        f"{'NAME':22s}"

        f"{'TYPE':18s}"

        f"{'ZONE':15s}"

        f"{'W':>6s}"

        f"{'H':>6s}"

        f"{'AREA':>10s}"
    )

    print(header)

    print("-" * len(header))

    for s in state.spaces:

        print(

            f"{s.name:22s}"

            f"{s.room_type:18s}"

            f"{s.zone:15s}"

            f"{s.width:6.1f}"

            f"{s.height:6.1f}"

            f"{s.area:10.1f}"
        )

    # =========================================================================
    # CIRCULATION
    # =========================================================================

    print("\n[CIRCULATION]")

    circulation_rooms = [

        s for s in state.spaces

        if any(

            k in s.name.lower()

            for k in [

                "living",

                "stair",

                "parking",

                "main_gate"
            ]
        )
    ]

    for s in circulation_rooms:

        print(

            f"  {s.name:20s}"

            f"{s.width:.1f}x{s.height:.1f}"
        )

    # =========================================================================
    # WET WALLS
    # =========================================================================

    print("\n[WET WALLS]")

    wet_rooms = [

        s for s in state.spaces

        if any(

            k in s.name

            for k in [

                "kitchen",

                "bathroom",

                "wash_area"
            ]
        )
    ]

    for s in wet_rooms:

        print(

            f"  {s.name:20s}"

            f"{s.zone:15s}"
        )

    # =========================================================================
    # EXTERIOR TOUCH
    # =========================================================================

    if state.buildable_polygon:

        exterior = state.buildable_polygon.boundary

        print("\n[EXTERIOR TOUCH]")

        for s in state.spaces:

            shared = (

                s.polygon.buffer(0.2).boundary.intersection(
                    exterior
                )
            )

            print(

                f"  {s.name:20s}"

                f"{shared.length:.1f} ft"
            )

    # =========================================================================
    # POLYGON INFO
    # =========================================================================

    print("\n[POLYGONS]")

    for s in state.spaces:

        poly = s.polygon

        geom_type = poly.geom_type

        compactness = polygon_compactness(
            poly
        )

        print(

            f"  {s.name:20s}"

            f"{geom_type:15s}"

            f"compact={compactness:.3f}"
        )

    # =========================================================================
    # RESIDUAL
    # =========================================================================

    residual = residual_space(state)

    print("\n[RESIDUAL SPACE]")

    print(

        f"  Residual Area      : "
        f"{residual.area:.1f} sqft"
    )

    print(

        f"  Residual Type      : "
        f"{residual.geom_type}"
    )

    # =========================================================================
    # ERRORS
    # =========================================================================

    if state.errors:

        print("\n[ERRORS]")

        for e in state.errors:

            print(f"  ❌ {e}")

    # =========================================================================
    # WARNINGS
    # =========================================================================

    if state.warnings:

        print("\n[WARNINGS]")

        for w in state.warnings:

            print(f"  ⚠ {w}")

    print("\n" + "=" * 80)

# =============================================================================
# COMPACTNESS
# =============================================================================


def polygon_compactness(

    poly
):

    if poly.area <= 0:

        return 0

    if poly.length <= 0:

        return 0

    return (

        4
        * 3.14159
        * poly.area

    ) / (

        poly.length ** 2
    )

# =============================================================================
# RESIDUAL SPACE
# =============================================================================


def residual_space(

    state
):

    if not state.buildable_polygon:

        return Polygon()

    topology_spaces = [

        s.polygon

        for s in state.spaces

        if s.zone != "environmental"
    ]

    if len(topology_spaces) == 0:

        return state.buildable_polygon

    from shapely.ops import unary_union

    occupied = unary_union(
        topology_spaces
    )

    return state.buildable_polygon.difference(
        occupied
    )

# =============================================================================
# OVERLAPS
# =============================================================================


def print_overlaps(

    state
):

    print("\n[OVERLAPS]")

    found = False

    for i in range(len(state.spaces)):

        for j in range(i + 1, len(state.spaces)):

            a = state.spaces[i]

            b = state.spaces[j]

            if not a.polygon.intersects(
                b.polygon
            ):

                continue

            inter = a.polygon.intersection(
                b.polygon
            )

            if inter.area < 1:

                continue

            found = True

            print(

                f"  {a.name}"

                f" ↔ "

                f"{b.name}"

                f" = "

                f"{inter.area:.2f} sqft"
            )

    if not found:

        print("  ✔ No overlaps")

# =============================================================================
# CONNECTIVITY
# =============================================================================


def print_connectivity(

    state
):

    print("\n[CONNECTIVITY]")

    for i in range(len(state.spaces)):

        a = state.spaces[i]

        connected = []

        for j in range(len(state.spaces)):

            if i == j:

                continue

            b = state.spaces[j]

            shared = (

                a.polygon.boundary.intersection(
                    b.polygon.boundary
                )
            )

            if shared.length >= 2:

                connected.append(
                    b.name
                )

        print(

            f"  {a.name:20s}"

            f"{connected}"
        )

# =============================================================================
# EXPORT DEBUG DATA
# =============================================================================


def export_debug_dict(

    state
):

    data = {

        "plot": {

            "width":
            state.plot_width,

            "height":
            state.plot_height,

            "facing":
            state.facing
        },

        "rooms": []
    }

    for s in state.spaces:

        data["rooms"].append({

            "name":
            s.name,

            "type":
            s.room_type,

            "zone":
            s.zone,

            "width":
            s.width,

            "height":
            s.height,

            "area":
            s.area,

            "bounds":
            s.polygon.bounds
        })

    return data