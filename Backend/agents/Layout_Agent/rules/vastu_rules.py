# =============================================================================
# TOPOLOGY-AWARE VASTU RULES
# =============================================================================
# Production Vastu intelligence engine
#
# IMPORTANT:
# Vastu is NOT strict corner locking.
#
# Vastu acts as:
# - directional preference scoring
# - topology guidance
# - environmental balancing
# - circulation orientation
#
# The solver should:
# prioritize > force
# =============================================================================

from typing import Dict

from config.room_standards import (

    VASTU_POSITIONS,

    MAIN_DOOR_POSITION,

    MAIN_GATE_POSITION,

    STAIR_VALID_CORNERS,

    KITCHEN_CORNERS
)

# =============================================================================
# ROOM POSITION
# =============================================================================


def get_preferred_position(

    room_type: str

):

    return VASTU_POSITIONS.get(
        room_type,
        "center"
    )

# =============================================================================
# MAIN DOOR
# =============================================================================


def main_door_position(

    facing: str

):

    return MAIN_DOOR_POSITION.get(
        facing.lower(),
        "north-east"
    )

# =============================================================================
# MAIN GATE
# =============================================================================


def main_gate_position(

    facing: str

):

    return MAIN_GATE_POSITION.get(
        facing.lower(),
        "north-east"
    )

# =============================================================================
# STAIRCASE
# =============================================================================


def staircase_positions():

    return STAIR_VALID_CORNERS

# =============================================================================
# KITCHEN
# =============================================================================


def kitchen_positions():

    return KITCHEN_CORNERS

# =============================================================================
# ROOM SCORES
# =============================================================================


def vastu_score(

    room_type: str,

    placed_zone: str

):

    preferred = get_preferred_position(
        room_type
    )

    # =====================================================
    # PERFECT
    # =====================================================

    if preferred == placed_zone:

        return 100

    # =====================================================
    # KITCHEN
    # =====================================================

    if room_type == "kitchen":

        if placed_zone == "north_west":

            return 80

    # =====================================================
    # STAIRCASE
    # =====================================================

    if room_type == "staircase":

        if placed_zone in [

            "south_west",

            "south_east",

            "north_west"
        ]:

            return 90

    # =====================================================
    # LIVING
    # =====================================================

    if room_type == "living":

        if placed_zone in [

            "north",

            "north_east"
        ]:

            return 90

    # =====================================================
    # BEDROOM
    # =====================================================

    if room_type in [

        "bedroom",
        "master_bedroom"
    ]:

        if placed_zone in [

            "south",
            "south_west",
            "west"
        ]:

            return 85

    # =====================================================
    # BATHROOM
    # =====================================================

    if room_type in [

        "bathroom",
        "attached_bathroom"
    ]:

        if placed_zone in [

            "west",
            "north_west"
        ]:

            return 80

    return 50

# =============================================================================
# TOPOLOGY PRIORITY
# =============================================================================


def vastu_priority():

    """
    Rooms with higher directional importance.
    """

    return {

        "kitchen": 5,

        "main_door": 5,

        "master_bedroom": 4,

        "living": 4,

        "staircase": 3,

        "bathroom": 2,

        "wash_area": 2
    }

# =============================================================================
# FLEXIBLE RULES
# =============================================================================


def flexible_vastu_rules():

    """
    Solver should treat these as preferences.
    """

    return {

        "kitchen_se_preferred":
        True,

        "kitchen_nw_allowed":
        True,

        "living_front_preferred":
        True,

        "master_southwest_preferred":
        True,

        "bathroom_west_preferred":
        True,

        "staircase_corner_preferred":
        True
    }

# =============================================================================
# ENVIRONMENTAL ORIENTATION
# =============================================================================


def environmental_orientation():

    return {

        "living_prefers_light":
        True,

        "bedroom_prefers_cross_ventilation":
        True,

        "wash_area_requires_exterior":
        True,

        "bathroom_requires_exhaust":
        True
    }

# =============================================================================
# ENTRY FLOW
# =============================================================================


def entry_flow_rules(

    facing: str

):

    facing = facing.lower()

    return {

        "road_facing":
        facing,

        "main_gate":
        main_gate_position(facing),

        "main_door":
        main_door_position(facing),

        "living_near_entry":
        True,

        "private_rooms_deeper":
        True
    }

# =============================================================================
# ZONE MAPPING
# =============================================================================


def directional_zone_map():

    return {

        "north_east":
        ["living", "lawn"],

        "south_east":
        ["kitchen", "wash_area", "store"],

        "south_west":
        ["master_bedroom", "staircase"],

        "north_west":
        ["bathroom", "guest_bedroom"],

        "center":
        ["living", "dining"]
    }

# =============================================================================
# TOPOLOGY FLOW
# =============================================================================


def vastu_topology_flow():

    """
    Ideal spatial progression.
    """

    return [

        "road",

        "gate",

        "lawn",

        "living",

        "dining",

        "kitchen",

        "private_cluster"
    ]

# =============================================================================
# VALIDATION
# =============================================================================


def validate_vastu_placement(

    room_type: str,

    zone: str,

    threshold: int = 70

):

    return vastu_score(
        room_type,
        zone
    ) >= threshold