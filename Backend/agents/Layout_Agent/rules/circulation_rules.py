# =============================================================================
# TOPOLOGY-AWARE CIRCULATION RULES
# =============================================================================
# Production circulation intelligence
#
# IMPORTANT:
# Circulation is NOT hallway generation.
#
# Circulation means:
# - topology flow
# - accessibility graph
# - entrance connectivity
# - social emergence
# - cluster transitions
# =============================================================================

from typing import Dict, List

from config.constants import *

# =============================================================================
# BASIC DIMENSIONS
# =============================================================================


def minimum_corridor_width():

    return CORRIDOR_MIN_W


def preferred_corridor_width():

    return CORRIDOR_PREF_W


def circulation_spine_width():

    return SPINE_MIN_WIDTH


def circulation_branch_width():

    return SPINE_BRANCH_WIDTH


def door_width():

    return BEDROOM_DOOR_W

# =============================================================================
# ROOM ACCESSIBILITY
# =============================================================================


def requires_direct_access(

    room_type: str

):

    """
    Rooms requiring direct circulation access.
    """

    required = [

        "living",

        "dining",

        "kitchen",

        "bedroom",

        "master_bedroom",

        "bathroom",

        "staircase"
    ]

    return room_type in required

# =============================================================================
# PRIVATE DEPTH
# =============================================================================


def privacy_depth(

    room_type: str

):

    """
    Higher value → deeper in topology.
    """

    mapping = {

        "living": 0,

        "dining": 1,

        "kitchen": 2,

        "bathroom": 2,

        "bedroom": 3,

        "master_bedroom": 4,
    }

    return mapping.get(
        room_type,
        1
    )

# =============================================================================
# SOCIAL FLOW
# =============================================================================


def social_transition_graph():

    """
    Social topology progression.
    """

    return {

        "entrance": [
            "living"
        ],

        "living": [
            "dining",
            "staircase"
        ],

        "dining": [
            "kitchen"
        ],

        "kitchen": [
            "wash_area",
            "store"
        ]
    }

# =============================================================================
# PRIVATE FLOW
# =============================================================================


def private_transition_graph():

    return {

        "corridor": [

            "bedroom",

            "master_bedroom"
        ],

        "bedroom": [

            "attached_bathroom"
        ],

        "master_bedroom": [

            "attached_bathroom"
        ]
    }

# =============================================================================
# CIRCULATION CLUSTERS
# =============================================================================


def circulation_clusters():

    return {

        "social_cluster": [

            "living",

            "dining"
        ],

        "service_cluster": [

            "kitchen",

            "wash_area",

            "store"
        ],

        "private_cluster": [

            "bedroom",

            "master_bedroom",

            "attached_bathroom"
        ]
    }

# =============================================================================
# CIRCULATION INTENT
# =============================================================================


def circulation_strategy(

    requirements: Dict

):

    bedrooms = requirements.get(
        "bedrooms",
        2
    )

    has_backyard = (

        "backyard"

        in

        requirements.get(
            "optional_rooms",
            []
        )
    )

    # =====================================================
    # CENTRAL SPINE
    # =====================================================

    if bedrooms >= 3:

        return {

            "type":
            "central_spine",

            "branching":
            True,

            "private_split":
            True,

            "service_branch":
            True
        }

    # =====================================================
    # LINEAR FLOW
    # =====================================================

    if has_backyard:

        return {

            "type":
            "environmental_spine",

            "backyard_connected":
            True,

            "service_court":
            True
        }

    # =====================================================
    # DEFAULT
    # =====================================================

    return {

        "type":
        "compact_flow",

        "branching":
        False
    }

# =============================================================================
# DOOR PLACEMENT FLOW
# =============================================================================


def preferred_entry_side(

    room_type: str

):

    """
    Architectural door logic.
    """

    mapping = {

        "living":
        "front",

        "dining":
        "living_connected",

        "kitchen":
        "dining_connected",

        "bedroom":
        "corridor_connected",

        "master_bedroom":
        "private_transition",

        "bathroom":
        "side_entry",

        "attached_bathroom":
        "bedroom_internal",

        "wash_area":
        "kitchen_rear"
    }

    return mapping.get(
        room_type,
        "corridor_connected"
    )

# =============================================================================
# ENVIRONMENTAL FLOW
# =============================================================================


def environmental_circulation_rules():

    """
    Open-space driven circulation.
    """

    return {

        "wash_area_requires_exterior":
        True,

        "bathroom_requires_ventilation":
        True,

        "living_prefers_front_open":
        True,

        "kitchen_prefers_service_court":
        True,

        "cross_ventilation_preferred":
        True
    }

# =============================================================================
# CONNECTIVITY VALIDATION
# =============================================================================


def minimum_shared_edge():

    """
    Minimum shared circulation edge.
    """

    return 3.0

# =============================================================================
# DEADSPACE PREVENTION
# =============================================================================


def deadspace_threshold():

    return MAX_DEADSPACE_PERCENTAGE

# =============================================================================
# TOPOLOGY PRIORITY
# =============================================================================


def topology_priority():

    """
    Architectural topology order.
    """

    return [

        "entrance",

        "parking",

        "lawn",

        "circulation",

        "service_cluster",

        "private_cluster",

        "living_emergence"
    ]