# =============================================================================
# GEOMETRY OPTIMIZER v20
# =============================================================================
# TOPOLOGY-AWARE ARCHITECTURAL VALIDATION ENGINE
#
# RESPONSIBILITIES
#
# ✔ compactness validation
# ✔ aspect ratio validation
# ✔ wet wall validation
# ✔ ventilation validation
# ✔ residual quality validation
# ✔ topology quality scoring
#
# STRICT RULES
#
# ✘ NO geometry mutation
# ✘ NO overlap fixing
# ✘ NO topology reinjection
# ✘ NO repair unions
#
# IMPORTANT
#
# This engine ONLY evaluates topology quality.
#
# It NEVER modifies geometry.
#
# =============================================================================

from typing import List

from shapely.geometry import (
    Polygon,
    MultiPolygon,
    GeometryCollection
)

from shapely.ops import unary_union

from state import Space

# =============================================================================
# CONSTANTS
# =============================================================================

MAX_ASPECT_RATIO = 3.8

MIN_COMPACTNESS = 0.20

MIN_EXTERIOR_TOUCH = 2.0

MIN_RESIDUAL_AREA = 35.0

# =============================================================================
# MAIN
# =============================================================================

def optimize_proportions(

    spaces: List[Space],

    buildable: Polygon
):

    print("\n" + "=" * 60)
    print("GEOMETRY OPTIMIZER v20")
    print("=" * 60)

    _validate_compactness(
        spaces
    )

    _validate_aspect_ratios(
        spaces
    )

    _validate_ventilation(
        spaces,
        buildable
    )

    _validate_wet_wall_clusters(
        spaces
    )

    _validate_residual_quality(
        spaces,
        buildable
    )

    print(
        "\n✔ Geometry validation complete"
    )

    return spaces

# =============================================================================
# COMPACTNESS
# =============================================================================

def _validate_compactness(

    spaces: List[Space]
):

    print("\n[COMPACTNESS]")

    for s in spaces:

        if s.polygon is None:
            continue

        if s.polygon.is_empty:
            continue

        if s.zone in (
            "frontage",
            "environmental"
        ):
            continue

        score = _compactness(
            s.polygon
        )

        if score < MIN_COMPACTNESS:

            print(

                f"  ⚠ {s.name:18s}"

                f"compactness={score:.2f}"
            )

# =============================================================================
# ASPECT RATIOS
# =============================================================================

def _validate_aspect_ratios(

    spaces: List[Space]
):

    print("\n[ASPECT RATIOS]")

    for s in spaces:

        if s.polygon is None:
            continue

        if s.polygon.is_empty:
            continue

        if s.zone in (
            "frontage",
            "environmental"
        ):
            continue

        minx, miny, maxx, maxy = (
            s.polygon.bounds
        )

        width = maxx - minx
        height = maxy - miny

        if min(width, height) <= 0:
            continue

        ratio = max(
            width,
            height
        ) / min(
            width,
            height
        )

        if ratio > MAX_ASPECT_RATIO:

            print(

                f"  ⚠ {s.name:18s}"

                f"ratio={ratio:.2f}"
            )

# =============================================================================
# VENTILATION
# =============================================================================

def _validate_ventilation(

    spaces,

    buildable
):

    print("\n[VENTILATION]")

    if buildable is None:
        return

    boundary = buildable.boundary

    for s in spaces:

        if s.zone in (
            "frontage",
            "environmental"
        ):
            continue

        if s.room_type in (
            "store"
        ):
            continue

        try:

            shared = (

                s.polygon.boundary
                .intersection(boundary)
            )

            if shared.length < MIN_EXTERIOR_TOUCH:

                print(

                    f"  ⚠ {s.name:18s}"

                    f"poor ventilation"
                )

        except Exception:
            continue

# =============================================================================
# WET WALL CLUSTERS
# =============================================================================

def _validate_wet_wall_clusters(

    spaces
):

    print("\n[WET WALL CLUSTERS]")

    wet = [

        s for s in spaces

        if s.room_type in (

            "kitchen",
            "bathroom",
            "wash_area",
            "utility"
        )
    ]

    for i in range(len(wet)):

        a = wet[i]

        aligned = False

        for j in range(i + 1, len(wet)):

            b = wet[j]

            try:

                shared = (

                    a.polygon.boundary
                    .intersection(
                        b.polygon.boundary
                    )
                )

                if shared.length >= 2:

                    aligned = True
                    break

            except Exception:
                continue

        if not aligned:

            print(

                f"  ⚠ {a.name:18s}"

                f"isolated wet zone"
            )

# =============================================================================
# RESIDUAL QUALITY
# =============================================================================

def _validate_residual_quality(

    spaces,

    buildable
):

    print("\n[RESIDUAL QUALITY]")

    if buildable is None:
        return

    indoor = []

    for s in spaces:

        if s.zone in (
            "frontage",
            "environmental"
        ):
            continue

        indoor.append(
            s.polygon
        )

    if not indoor:
        return

    try:

        used = unary_union(
            indoor
        )

        residual = buildable.difference(
            used
        )

    except Exception:

        return

    residual = _clean_geometry(
        residual
    )

    if residual is None:
        return

    # -------------------------------------------------------------------------
    # MULTI
    # -------------------------------------------------------------------------

    if isinstance(
        residual,
        MultiPolygon
    ):

        for poly in residual.geoms:

            if poly.area < MIN_RESIDUAL_AREA:

                print(

                    f"  ⚠ tiny residual"

                    f" ({poly.area:.1f})"
                )

    # -------------------------------------------------------------------------
    # SINGLE
    # -------------------------------------------------------------------------

    else:

        if residual.area < MIN_RESIDUAL_AREA:

            print(

                f"  ⚠ poor residual"

                f" ({residual.area:.1f})"
            )

# =============================================================================
# COMPACTNESS SCORE
# =============================================================================

def _compactness(

    polygon
):

    try:

        area = polygon.area

        perimeter = polygon.length

        if perimeter <= 0:
            return 0

        return (

            4
            *
            3.14159
            *
            area

            /

            (perimeter ** 2)
        )

    except Exception:

        return 0

# =============================================================================
# CLEAN GEOMETRY
# =============================================================================

def _clean_geometry(

    geometry
):

    if geometry is None:
        return None

    if geometry.is_empty:
        return None

    try:

        geometry = geometry.buffer(0)

    except Exception:

        return None

    if geometry.is_empty:
        return None

    # -------------------------------------------------------------------------
    # GEOMETRY COLLECTION
    # -------------------------------------------------------------------------

    if isinstance(
        geometry,
        GeometryCollection
    ):

        polys = []

        for g in geometry.geoms:

            if isinstance(
                g,
                Polygon
            ):

                if g.area >= MIN_RESIDUAL_AREA:

                    polys.append(g)

        if not polys:
            return None

        geometry = unary_union(
            polys
        )

    # -------------------------------------------------------------------------
    # MULTI POLYGON
    # -------------------------------------------------------------------------

    if isinstance(
        geometry,
        MultiPolygon
    ):

        valid = []

        for p in geometry.geoms:

            if p.area >= MIN_RESIDUAL_AREA:

                valid.append(p)

        if not valid:
            return None

        geometry = max(
            valid,
            key=lambda g: g.area
        )

    return geometry