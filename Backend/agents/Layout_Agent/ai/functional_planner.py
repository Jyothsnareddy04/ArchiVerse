from typing import Dict, Any


class FunctionalPlanner:

    """
    Converts LLM topology intent into
    percentage-based architectural planning.
    """

    def generate_area_distribution(
        self,
        requirements: Dict[str, Any]
    ) -> Dict:

        bedrooms = requirements.get(
            "bedrooms",
            2
        )

        optional = requirements.get(
            "optional_rooms",
            []
        )

        # =================================================
        # BASE DISTRIBUTION
        # =================================================

        plan = {

            "social_percentage": 32,

            "private_percentage": 42,

            "service_percentage": 18,

            "circulation_percentage": 8,
        }

        # =================================================
        # BEDROOM ADJUSTMENT
        # =================================================

        if bedrooms >= 3:

            plan["private_percentage"] += 5
            plan["social_percentage"] -= 3

        # =================================================
        # OPTIONAL ROOMS
        # =================================================

        if "dining" in optional:

            plan["social_percentage"] += 4

        if "store" in optional:

            plan["service_percentage"] += 2

        if "backyard" in optional:

            plan["circulation_percentage"] += 2

        # =================================================
        # NORMALIZE
        # =================================================

        total = sum(plan.values())

        for k in plan:

            plan[k] = round(
                (plan[k] / total) * 100,
                2
            )

        print("\n  [FUNCTIONAL PLAN]")

        for k, v in plan.items():

            print(f"    {k}: {v}%")

        return plan
    
# =============================================================================
# COMPUTE ROOM LIST
# =============================================================================

from typing import (
    Dict,
    Any,
    List
)

from config.room_standards import (
    ROOM_STANDARDS
)

# =============================================================================
# MAIN
# =============================================================================


def compute_room_list(

    requirements,

    buildable_width=None,

    buildable_height=None,

    topology=None,

    llm_plan=None
)-> List[Dict[str, Any]]:

    bedrooms = requirements.get(
        "bedrooms",
        2
    )

    bathrooms = requirements.get(
        "bathrooms",
        2
    )

    optional = requirements.get(
        "optional_rooms",
        []
    )

    rooms = []

    
    # =========================================================================
    # BUILDABLE INFO
    # =========================================================================

    if buildable_width and buildable_height:

        buildable_area = (

            buildable_width *

            buildable_height
        )

    else:

        buildable_area = 0
    # =========================================================================
    # LIVING
    # =========================================================================

    rooms.append(

        _room(
            "living",
            "living"
        )
    )

    # =========================================================================
    # DINING
    # =========================================================================

    if "dining" in optional:

        rooms.append(

            _room(
                "dining",
                "dining"
            )
        )

    # =========================================================================
    # KITCHEN
    # =========================================================================

    rooms.append(

        _room(
            "kitchen",
            "kitchen"
        )
    )

    # =========================================================================
    # MASTER
    # =========================================================================

    rooms.append(

        _room(
            "master_bedroom",
            "master_bedroom"
        )
    )

    # =========================================================================
    # BEDROOMS
    # =========================================================================

    for i in range(
        bedrooms - 1
    ):

        rooms.append(

            _room(
                f"bedroom_{i+1}",
                "bedroom"
            )
        )

    # =========================================================================
    # BATHROOMS
    # =========================================================================

    for i in range(
        bathrooms
    ):

        rooms.append(

            _room(
                f"bathroom_{i+1}",
                "bathroom"
            )
        )

    # =========================================================================
    # STORE
    # =========================================================================

    if "store" in optional:

        rooms.append(

            _room(
                "store",
                "store"
            )
        )

    # =========================================================================
    # BACKYARD
    # =========================================================================

    if "backyard" in optional:

        rooms.append(

            _room(
                "backyard",
                "backyard"
            )
        )

    # =========================================================================
    # WASH AREA
    # =========================================================================

    rooms.append(

        _room(
            "wash_area",
            "wash_area"
        )
    )

    return rooms

# =============================================================================
# ROOM
# =============================================================================


def _room(

    name,

    room_type
):

    std = ROOM_STANDARDS.get(

        room_type,

        {}
    )

    return {

        "name": name,

        "type": room_type,

        "width": std.get(

            "pref_w",

            10
        ),

        "height": std.get(

            "pref_h",

            10
        ),

        "min_width": std.get(

            "min_w",

            8
        ),

        "min_height": std.get(

            "min_h",

            8
        ),

        "zone": std.get(

            "zone",

            "semi_private"
        )
    }