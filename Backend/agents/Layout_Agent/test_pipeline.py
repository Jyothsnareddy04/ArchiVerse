# =============================================================================
# ARCHIVERSE PRODUCTION TEST SUITE v12
# =============================================================================
# SEMANTIC + TOPOLOGY VALIDATION ENGINE
# =============================================================================

import os
import sys
import traceback

ROOT_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

if ROOT_DIR not in sys.path:

    sys.path.insert(
        0,
        ROOT_DIR
    )

from pipeline import run_pipeline

# =============================================================================
# TEST CASES
# =============================================================================

TEST_CASES = [

    {
        "name": "40x60 North 2BHK",
        "input": {
            "plot": (40, 60),
            "facing": "north",
            "bedrooms": 2,
            "bathrooms": 2,
            "parking": True,
            "lawn": True,
            "plants": True,
            "optional_rooms": [
                "store",
                "backyard",
                "dining"
            ]
        }
    },

    {
        "name": "45x65 East 2BHK",
        "input": {
            "plot": (45, 65),
            "facing": "east",
            "bedrooms": 2,
            "bathrooms": 2,
            "parking": True,
            "lawn": True,
            "plants": True,
            "optional_rooms": [
                "store",
                "backyard",
                "dining"
            ]
        }
    },

    {
        "name": "50x70 South 3BHK",
        "input": {
            "plot": (50, 70),
            "facing": "south",
            "bedrooms": 3,
            "bathrooms": 3,
            "parking": True,
            "lawn": True,
            "plants": True,
            "optional_rooms": [
                "store",
                "backyard",
                "dining"
            ]
        }
    },

    {
        "name": "45x70 West 3BHK",
        "input": {
            "plot": (45, 70),
            "facing": "west",
            "bedrooms": 3,
            "bathrooms": 3,
            "parking": True,
            "lawn": True,
            "plants": True,
            "optional_rooms": [
                "store",
                "backyard",
                "dining"
            ]
        }
    }
]
# =============================================================================
# HELPERS
# =============================================================================

def get_spaces(

    variant,

    room_type
):

    return [

        s for s in variant.spaces

        if s.room_type == room_type
    ]


def get_first(

    variant,

    room_type
):

    spaces = get_spaces(
        variant,
        room_type
    )

    if spaces:
        return spaces[0]

    return None


# =============================================================================
# CORNER CHECK
# =============================================================================

def near_corner(

    point_x,
    point_y,

    target_x,
    target_y,

    bw,
    bh
):

    return (

        abs(point_x - target_x) < bw * 0.25

        and

        abs(point_y - target_y) < bh * 0.25
    )

# =============================================================================
# FACING TOPOLOGY VALIDATION
# =============================================================================

def validate_facing_topology(

    variant
):

    facing = variant.facing.lower()

    buildable = variant.buildable_polygon

    bx0, by0, bx1, by1 = (
        buildable.bounds
    )

    bw = bx1 - bx0
    bh = by1 - by0

    master = get_first(
        variant,
        "master_bedroom"
    )

    kitchen = get_first(
        variant,
        "kitchen"
    )

    parking = get_first(
        variant,
        "parking"
    )

    bedrooms = get_spaces(
        variant,
        "bedroom"
    )

    checks = {

        "master_position": False,

        "secondary_position": False,

        "kitchen_position": False,

        "parking_position": False
    }

    # =========================================================================
    # MASTER
    # =========================================================================

    if master:

        cx = master.centroid.x
        cy = master.centroid.y

        # -------------------------------------------------------------
        # SOUTH -> NE
        # OTHERS -> SW
        # -------------------------------------------------------------

        if facing == "south":

            checks["master_position"] = near_corner(

                cx,
                cy,

                bx1,
                by1,

                bw,
                bh
            )

        else:

            checks["master_position"] = near_corner(

                cx,
                cy,

                bx0,
                by0,

                bw,
                bh
            )

    # =========================================================================
    # KITCHEN
    # =========================================================================

    if kitchen:

        cx = kitchen.centroid.x
        cy = kitchen.centroid.y

        if facing in [

            "north",
            "east",
            "west"
        ]:

            checks["kitchen_position"] = near_corner(

                cx,
                cy,

                bx1,
                by0,

                bw,
                bh
            )

        else:

            checks["kitchen_position"] = near_corner(

                cx,
                cy,

                bx0,
                by1,

                bw,
                bh
            )

    # =========================================================================
    # PARKING
    # =========================================================================

    if parking:

        cx = parking.centroid.x
        cy = parking.centroid.y

        if facing == "north":

            checks["parking_position"] = near_corner(

                cx,
                cy,

                bx1,
                by1,

                bw,
                bh
            )

        elif facing == "south":

            checks["parking_position"] = near_corner(

                cx,
                cy,

                bx1,
                by0,

                bw,
                bh
            )

        elif facing == "east":

            checks["parking_position"] = near_corner(

                cx,
                cy,

                bx1,
                by1,

                bw,
                bh
            )

        else:

            checks["parking_position"] = near_corner(

                cx,
                cy,

                bx0,
                by1,

                bw,
                bh
            )

    # =========================================================================
    # SECONDARY BEDROOMS
    # =========================================================================

    secondary_ok = True

    for b in bedrooms:

        cx = b.centroid.x
        cy = b.centroid.y

        valid = False

        # -------------------------------------------------------------
        # NORTH
        # -------------------------------------------------------------

        if facing == "north":

            valid = (

                near_corner(
                    cx, cy,
                    bx0, by1,
                    bw, bh
                )

                or

                (
                    cx > bx1 - bw * 0.30
                    and
                    cy > by0 + bh * 0.45
                )
            )

        # -------------------------------------------------------------
        # EAST
        # -------------------------------------------------------------

        elif facing == "east":

            valid = near_corner(

                cx,
                cy,

                bx0,
                by1,

                bw,
                bh
            )

        # -------------------------------------------------------------
        # SOUTH
        # -------------------------------------------------------------

        elif facing == "south":

            valid = (

                near_corner(
                    cx, cy,
                    bx0, by1,
                    bw, bh
                )

                or

                (
                    cx > bx1 - bw * 0.30
                    and
                    cy < by1 - bh * 0.35
                    and
                    cy > by0 + bh * 0.35
                )
            )

        # -------------------------------------------------------------
        # WEST
        # -------------------------------------------------------------

        else:

            valid = near_corner(

                cx,
                cy,

                bx1,
                by1,

                bw,
                bh
            )

        if not valid:

            secondary_ok = False

    checks["secondary_position"] = secondary_ok

    return checks

# =============================================================================
# ADJACENCY
# =============================================================================

def validate_adjacency(

    variant
):

    checks = {

        "dining_adjacent_kitchen": False,

        "utility_adjacent_kitchen": False,

        "wash_adjacent_utility": False
    }

    kitchen = get_first(
        variant,
        "kitchen"
    )

    dining = get_first(
        variant,
        "dining"
    )

    utility = get_first(
        variant,
        "utility"
    )

    wash = get_first(
        variant,
        "wash_area"
    )

    if kitchen and dining:

        checks["dining_adjacent_kitchen"] = (

            kitchen.polygon.distance(
                dining.polygon
            ) < 2
        )

    if kitchen and utility:

        checks["utility_adjacent_kitchen"] = (

            kitchen.polygon.distance(
                utility.polygon
            ) < 2
        )

    if utility and wash:

        checks["wash_adjacent_utility"] = (

            utility.polygon.distance(
                wash.polygon
            ) < 2
        )

    return checks

# =============================================================================
# MAIN VALIDATOR
# =============================================================================

def validate_variant(

    variant,

    test_input
):

    checks = {}

    # =========================================================================
    # ROOM TYPES
    # =========================================================================

    room_types = [

        s.room_type

        for s in variant.spaces
    ]

    # =========================================================================
    # CORE
    # =========================================================================

    checks["kitchen"] = (
        "kitchen" in room_types
    )

    checks["master_bedroom"] = (
        "master_bedroom" in room_types
    )

    checks["parking"] = (
        "parking" in room_types
    )

    # =========================================================================
    # COUNTS
    # =========================================================================

    expected_bedrooms = (
        test_input["bedrooms"]
    )

    expected_bathrooms = (
        test_input["bathrooms"]
    )

    # ---------------------------------------------------------
    # MASTER + SECONDARY
    # ---------------------------------------------------------

    actual_bedrooms = sum(

        1 for s in variant.spaces

        if s.room_type in [

            "master_bedroom",
            "bedroom"
        ]
    )

    actual_bathrooms = sum(

        1 for s in variant.spaces

        if "bathroom" in s.room_type
    )

    checks["bedroom_count"] = (

        actual_bedrooms

        ==

        expected_bedrooms
    )

    checks["bathroom_count"] = (

        actual_bathrooms

        ==

        expected_bathrooms
    )

    # ---------------------------------------------------------
    # DEBUG
    # ---------------------------------------------------------

    print(

        f"  expected bedrooms : "
        f"{expected_bedrooms}"
    )

    print(

        f"  actual bedrooms   : "
        f"{actual_bedrooms}"
    )

    print(

        f"  expected bathrooms: "
        f"{expected_bathrooms}"
    )

    print(

        f"  actual bathrooms  : "
        f"{actual_bathrooms}"
    )

    # =========================================================================
    # BUILDABLE VALIDATION
    # =========================================================================

    checks["inside_buildable"] = True

    buildable = variant.buildable_polygon

    for s in variant.spaces:

        if s.zone == "environmental":
            continue

        if s.room_type in [

            "utility",
            "wash_area"
        ]:
            continue

        try:

            ok = buildable.contains(
                s.polygon.buffer(-0.05)
            )

            if not ok:

                checks["inside_buildable"] = False

        except:
            pass

    # =========================================================================
    # OVERLAP VALIDATION
    # =========================================================================

    overlap_ok = True

    IGNORE = {

        ("kitchen", "store"),
        ("store", "kitchen"),

        ("kitchen", "dining"),
        ("dining", "kitchen"),

        ("utility", "wash_area"),
        ("wash_area", "utility")
    }

    for i in range(len(variant.spaces)):

        for j in range(i + 1, len(variant.spaces)):

            a = variant.spaces[i]
            b = variant.spaces[j]

            if (
                a.room_type,
                b.room_type
            ) in IGNORE:

                continue

            inter = a.polygon.intersection(
                b.polygon
            )

            if inter.area > 1.0:

                overlap_ok = False

    checks["overlaps"] = overlap_ok

    # =========================================================================
    # UTILISATION
    # =========================================================================

    checks["utilisation"] = (
        variant.utilisation > 0.45
    )

    # =========================================================================
    # TOPOLOGY SCORE
    # =========================================================================

    checks["score"] = (
        variant.score >= 50
    )

    # =========================================================================
    # WALLS
    # =========================================================================

    checks["walls"] = hasattr(
        variant,
        "walls"
    )

    # =========================================================================
    # FACING TOPOLOGY
    # =========================================================================

    topology = validate_facing_topology(
        variant
    )

    checks.update(topology)

    # =========================================================================
    # ADJACENCY
    # =========================================================================

    adjacency = validate_adjacency(
        variant
    )

    checks.update(adjacency)

    return checks

# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":

    if sys.platform == "win32":

        sys.stdout.reconfigure(

            encoding="utf-8",

            errors="replace"
        )

        sys.stderr.reconfigure(

            encoding="utf-8",

            errors="replace"
        )

    print("\n" + "=" * 90)

    print(" ARCHIVERSE PRODUCTION TEST SUITE v12 ")

    print("=" * 90)

    total_tests = 0
    passed_tests = 0

    for tc in TEST_CASES:

        print("\n" + "#" * 90)

        print(f" TEST : {tc['name']} ")

        print("#" * 90)

        try:

            variants = run_pipeline(

                tc["input"],

                render=True
            )

            test_passed = False

            variant = variants[0]

            print("\n" + "-" * 70)

            print(" FINAL LAYOUT ")

            print("-" * 70)

            checks = validate_variant(

                variant,

                tc["input"]
            )

            passed = 0

            for k, v in checks.items():

                status = "PASS" if v else "FAIL"

                print(

                    f"  {k:35s}"
                    f"{status}"
                )

                if v:
                    passed += 1

            total = len(checks)

            final_score = (

                passed / total
            ) * 100

            print("\n")

            print(
                f"  VALIDATION SCORE : "
                f"{final_score:.1f}%"
            )

            print(
                f"  PIPELINE SCORE   : "
                f"{variant.score}"
            )

            print(
                f"  UTILISATION      : "
                f"{variant.utilisation*100:.1f}%"
            )

            print(
                f"  TOTAL SPACES     : "
                f"{len(variant.spaces)}"
            )

            print(
                f"  WARNINGS         : "
                f"{len(variant.warnings)}"
            )

            print(
                f"  ERRORS           : "
                f"{len(variant.errors)}"
            )

            # =============================================================================
            # PASS THRESHOLD
            # =============================================================================

            if final_score >= 80:

                test_passed = True

            total_tests += 1

            if test_passed:

                passed_tests += 1

                print("\n[FINAL RESULT] PASS")

            else:

                print("\n[FINAL RESULT] FAIL")

        except Exception as e:

            total_tests += 1

            print("\n[PIPELINE FAILURE]")

            print(e)

            traceback.print_exc()

    # =========================================================================
    # SUMMARY
    # =========================================================================

    print("\n" + "=" * 90)

    print(" FINAL SUMMARY ")

    print("=" * 90)

    print(

        f"\nTOTAL TESTS : {total_tests}"

        f"\nPASSED      : {passed_tests}"

        f"\nFAILED      : {total_tests - passed_tests}"
    )

    print("\n" + "=" * 90)