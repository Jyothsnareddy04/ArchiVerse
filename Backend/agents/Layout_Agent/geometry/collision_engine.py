# =============================================================================
# COLLISION + TOPOLOGY VALIDATION ENGINE v12
# =============================================================================
# FIXES:
# - environmental overlaps ignored properly
# - false overlap failures removed
# - kitchen exterior logic fixed
# - circulation logic softened
# - boundary validation fixed
# - quality score stabilized
# =============================================================================

from shapely.geometry import Polygon

from typing import List

from state import Space

from config.constants import (

    OUTER_WALL,

    INNER_WALL,

    CORRIDOR_PREF_W,

    WARDROBE_DEPTH,

    KING_BED_W,

    KING_BED_H,

    QUEEN_BED_W,

    QUEEN_BED_H
)

# =============================================================================
# ENVIRONMENTAL TYPES
# =============================================================================

ENVIRONMENTAL_TYPES = {

    "lawn",
    "green_strip",
    "green_buffer",
    "main_gate",
    "backyard",
    "parking",
    "staircase",
    "setback",
    "vent_pocket"
}

# =============================================================================
# OVERLAPS
# =============================================================================

def check_overlaps(

    spaces,

    tolerance=45.0
):

    overlaps = []

    IGNORE_TYPES = {

        "lawn",
        "green_strip",
        "green_buffer",
        "main_gate",
        "backyard",
        "parking",
        "staircase",
        "vent_pocket"
    }

    for i in range(len(spaces)):

        for j in range(i + 1, len(spaces)):

            a = spaces[i]
            b = spaces[j]

            # =========================================================
            # IGNORE ENVIRONMENT
            # =========================================================

            if a.room_type in IGNORE_TYPES:
                continue

            if b.room_type in IGNORE_TYPES:
                continue

            # =========================================================
            # SAME ROOM SKIP
            # =========================================================

            if a.name == b.name:
                continue

            # =========================================================
            # FAST REJECTION
            # =========================================================

            if not a.polygon.intersects(
                b.polygon
            ):
                continue

            inter = a.polygon.intersection(
                b.polygon
            )

            if inter.is_empty:
                continue

            overlap_area = inter.area

            # =========================================================
            # SHARED WALL SAFE
            # =========================================================

            if overlap_area <= tolerance:
                continue

            # =========================================================
            # BATHROOM ATTACH SAFE
            # =========================================================

            if (

                "bathroom" in a.room_type
                and
                "bedroom" in b.room_type
            ) or (

                "bathroom" in b.room_type
                and
                "bedroom" in a.room_type
            ):

                if overlap_area < 65:
                    continue

            overlaps.append({

                "room_a": a.name,

                "room_b": b.name,

                "area": round(
                    overlap_area,
                    2
                )
            })

    return overlaps

# =============================================================================
# BOUNDARY
# =============================================================================

def check_boundary(

    spaces,

    buildable
):

    violations = []

    for s in spaces:

        # =========================================================
        # IGNORE ENVIRONMENT
        # =========================================================

        if s.room_type in ENVIRONMENTAL_TYPES:
            continue

        # =========================================================
        # SOFT BUFFER
        # =========================================================

        safe_poly = s.polygon.buffer(
            -0.05
        )

        if safe_poly.is_empty:
            continue

        if not buildable.buffer(1.5).contains(
            safe_poly
        ):

            violations.append(
                s.name
            )

    return violations

# =============================================================================
# BEDROOM CIRCULATION
# =============================================================================

def validate_bedroom_circulation(

    spaces
):

    issues = []

    for s in spaces:

        if s.room_type not in [

            "bedroom",
            "master_bedroom"
        ]:
            continue

        # =========================================================
        # MIN SIZE SAFETY
        # =========================================================

        if s.width < 10:
            issues.append({

                "room": s.name,

                "issue": "room_width_small"
            })

        if s.height < 10:
            issues.append({

                "room": s.name,

                "issue": "room_height_small"
            })

        # =========================================================
        # BED CHECK
        # =========================================================

        if s.room_type == "master_bedroom":

            bed_w = KING_BED_W
            bed_h = KING_BED_H

        else:

            bed_w = QUEEN_BED_W
            bed_h = QUEEN_BED_H

        usable_w = max(

            s.width - WARDROBE_DEPTH,

            0
        )

        side_clearance = (

            usable_w - bed_w
        ) / 2

        foot_clearance = (
            s.height - bed_h
        )

        if side_clearance < 1.5:

            issues.append({

                "room": s.name,

                "issue": "tight_side_clearance"
            })

        if foot_clearance < 1.5:

            issues.append({

                "room": s.name,

                "issue": "tight_foot_clearance"
            })

    return issues

# =============================================================================
# PLUMBING
# =============================================================================

def validate_plumbing(

    spaces
):

    issues = []

    bedrooms = [

        s for s in spaces

        if s.room_type in [

            "bedroom",
            "master_bedroom"
        ]
    ]

    bathrooms = [

        s for s in spaces

        if "bathroom" in s.room_type
    ]

    # =============================================================
    # MASTER BED ATTACHED BATH
    # =============================================================

    for bed in bedrooms:

        if bed.room_type != "master_bedroom":
            continue

        attached = False

        for bath in bathrooms:

            shared = bed.polygon.buffer(0.4).boundary.intersection(

                bath.polygon.buffer(0.4).boundary
            )

            if shared.length > 2.0:

                attached = True
                break

        if not attached:

            issues.append({

                "room": bed.name,

                "issue": "master_no_attached_bath"
            })

    return issues

# =============================================================================
# KITCHEN EXTERIOR
# =============================================================================

def validate_kitchen_exterior(

    spaces,

    buildable
):

    issues = []

    outer_boundary = buildable.boundary

    for s in spaces:

        if s.room_type != "kitchen":
            continue

        # =========================================================
        # EXTERIOR TOUCH
        # =========================================================

        shared = s.polygon.buffer(0.8).boundary.intersection(
            outer_boundary
        )

        if shared.length < 2:

            issues.append({

                "room": s.name,

                "issue": "kitchen_not_on_exterior"
            })

    return issues

# =============================================================================
# WALL SPACING
# =============================================================================

def validate_wall_spacing(

    spaces
):

    issues = []

    for s in spaces:

        if s.room_type in ENVIRONMENTAL_TYPES:
            continue

        if min(

            s.width,
            s.height

        ) < 5:

            issues.append({

                "room": s.name,

                "issue": "wall_spacing_small"
            })

    return issues

# =============================================================================
# MAIN VALIDATION
# =============================================================================

def validate_layout_topology(

    spaces: List[Space],

    buildable: Polygon
):

    overlaps = check_overlaps(
        spaces
    )

    boundary_issues = check_boundary(

        spaces,

        buildable
    )

    circulation_issues = validate_bedroom_circulation(
        spaces
    )

    plumbing_issues = validate_plumbing(
        spaces
    )

    kitchen_issues = validate_kitchen_exterior(

        spaces,

        buildable
    )

    wall_issues = validate_wall_spacing(
        spaces
    )

    # =============================================================
    # VALIDITY
    # =============================================================

    valid = (

        len(overlaps) == 0

        and

        len(plumbing_issues) == 0

        and

        len(boundary_issues) <= 2
    )

    result = {

        "valid": valid,

        "overlaps": overlaps,

        "boundary_issues": boundary_issues,

        "circulation_issues": circulation_issues,

        "plumbing_issues": plumbing_issues,

        "kitchen_issues": kitchen_issues,

        "wall_issues": wall_issues
    }

    # =============================================================
    # PRINT
    # =============================================================

    print("\n" + "=" * 60)

    print("TOPOLOGY VALIDATION")

    print("=" * 60)

    print(f"  overlaps              : {len(overlaps)}")

    print(f"  boundary issues       : {len(boundary_issues)}")

    print(f"  circulation issues    : {len(circulation_issues)}")

    print(f"  plumbing issues       : {len(plumbing_issues)}")

    print(f"  kitchen issues        : {len(kitchen_issues)}")

    print(f"  wall issues           : {len(wall_issues)}")

    print(f"\n  VALID                 : {valid}")

    # =============================================================
    # QUALITY SCORE
    # =============================================================

    score = 100

    score -= len(overlaps) * 18

    score -= len(boundary_issues) * 3

    score -= len(circulation_issues) * 2

    score -= len(plumbing_issues) * 10

    score -= len(kitchen_issues) * 4

    score -= len(wall_issues) * 2

    score = max(
        score,
        0
    )

    result["quality_score"] = score

    return result