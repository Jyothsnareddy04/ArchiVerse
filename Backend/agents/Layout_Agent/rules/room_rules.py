# =============================================================================
# TOPOLOGY-AWARE ROOM RULES v4
# =============================================================================
# Production architectural intelligence layer
#
# Handles:
# - topology hierarchy
# - circulation logic
# - plumbing clustering
# - environmental openings
# - vastu positioning
# - adjacency priorities
# =============================================================================

from typing import Dict
from typing import Tuple
from typing import List

from config.room_standards import (

    ROOM_STANDARDS,

    VASTU_POSITIONS
)

from config.constants import *

# =============================================================================
# TOPOLOGY CLUSTERS
# =============================================================================

TOPOLOGY_CLUSTERS = {

    "social_cluster": [

        "living",

        "dining"
    ],

    "private_cluster": [

        "master_bedroom",

        "bedroom"
    ],

    "service_cluster": [

        "kitchen",

        "wash_area",

        "store",

        "bathroom"
    ],

    "environmental_cluster": [

        "lawn",

        "backyard",

        "balcony",

        "parking"
    ]
}

# =============================================================================
# DIMENSIONS
# =============================================================================


def get_min_dimensions(

    room_type: str

) -> Tuple[float, float]:

    std = ROOM_STANDARDS.get(

        room_type,

        {
            "min_w": 5,
            "min_h": 5
        }
    )

    return (

        std["min_w"],

        std["min_h"]
    )

# =============================================================================
# PREFERRED
# =============================================================================


def get_preferred_dimensions(

    room_type: str

):

    std = ROOM_STANDARDS.get(

        room_type,

        {
            "pref_w": 8,
            "pref_h": 8
        }
    )

    return (

        std["pref_w"],

        std["pref_h"]
    )

# =============================================================================
# AREA
# =============================================================================


def get_min_area(

    room_type: str

):

    w, h = get_min_dimensions(
        room_type
    )

    return w * h * 0.8

# =============================================================================
# ROOM VALIDATION
# =============================================================================


def validate_room_size(

    room_type: str,

    width: float,

    height: float
):

    min_w, min_h = get_min_dimensions(
        room_type
    )

    if width < min_w:

        return False

    if height < min_h:

        return False

    area = width * height

    if area < get_min_area(room_type):

        return False

    ratio = max(

        width,
        height

    ) / max(

        min(width, height),
        1
    )

    if ratio > 4:

        return False

    return True

# =============================================================================
# ROOM ZONE
# =============================================================================


def get_room_zone(

    room_type: str
):

    social = [

        "living"
    ]

    service = [

        "kitchen",

        "wash_area",

        "store",

        "bathroom"
    ]

    private = [

        "bedroom",

        "master_bedroom"
    ]

    semi_private = [

        "dining",

        "balcony",

        "parking",

        "staircase"
    ]

    if room_type in social:

        return "social"

    if room_type in service:

        return "service"

    if room_type in private:

        return "private"

    if room_type in semi_private:

        return "semi_private"

    return "semi_private"

# =============================================================================
# ROOM CLUSTER
# =============================================================================


def get_room_cluster(

    room_type: str
):

    for cluster, rooms in TOPOLOGY_CLUSTERS.items():

        if room_type in rooms:

            return cluster

    return "misc_cluster"

# =============================================================================
# PLACEMENT RULES
# =============================================================================


def get_placement_rules(

    room_type: str
):

    rules = {

        # =============================================================
        # KITCHEN
        # =============================================================

        "kitchen": {

            "near": [

                "dining",

                "wash_area",

                "store"
            ],

            "away_from": [

                "master_bedroom"
            ],

            "prefer_attach_to":
            "wash_area",

            "privacy_depth":
            1
        },

        # =============================================================
        # WASH AREA
        # =============================================================

        "wash_area": {

            "near": [

                "kitchen"
            ],

            "prefer_attach_to":
            "kitchen",

            "privacy_depth":
            1
        },

        # =============================================================
        # STORE
        # =============================================================

        "store": {

            "near": [

                "kitchen"
            ],

            "prefer_attach_to":
            "kitchen",

            "privacy_depth":
            1
        },

        # =============================================================
        # LIVING
        # =============================================================

        "living": {

            "near": [

                "dining",

                "parking",

                "staircase",

                "lawn"
            ],

            "privacy_depth":
            1
        },

        # =============================================================
        # MASTER
        # =============================================================

        "master_bedroom": {

            "near": [

                "attached_bathroom"
            ],

            "away_from": [

                "parking"
            ],

            "privacy_depth":
            4
        },

        # =============================================================
        # BEDROOM
        # =============================================================

        "bedroom": {

            "near": [

                "bathroom"
            ],

            "away_from": [

                "parking"
            ],

            "privacy_depth":
            3
        },

        # =============================================================
        # BATHROOM
        # =============================================================

        "bathroom": {

            "near": [

                "bedroom"
            ],

            "privacy_depth":
            2
        },

        # =============================================================
        # DINING
        # =============================================================

        "dining": {

            "near": [

                "living",

                "kitchen"
            ],

            "privacy_depth":
            2
        },

        # =============================================================
        # STAIRCASE
        # =============================================================

        "staircase": {

            "near": [

                "parking",

                "living"
            ],

            "privacy_depth":
            1
        }
    }

    return rules.get(
        room_type,
        {}
    )

# =============================================================================
# REQUIRED CONNECTIONS
# =============================================================================


def required_connections(

    room_type: str
):

    rules = get_placement_rules(
        room_type
    )

    result = []

    result.extend(

        rules.get(
            "near",
            []
        )
    )

    must_attach = rules.get(
        "prefer_attach_to"
    )

    if must_attach:

        result.append(
            must_attach
        )

    return result

# =============================================================================
# AVOID
# =============================================================================


def avoid_connections(

    room_type: str
):

    rules = get_placement_rules(
        room_type
    )

    return rules.get(
        "away_from",
        []
    )

# =============================================================================
# EXTERIOR
# =============================================================================


def requires_exterior_touch(

    room_type: str
):

    rules = get_placement_rules(
        room_type
    )

    return rules.get(

        "exterior_touch_required",

        False
    )

# =============================================================================
# VASTU
# =============================================================================


def preferred_vastu_position(

    room_type: str
):

    return VASTU_POSITIONS.get(

        room_type,

        "center"
    )

# =============================================================================
# BEDROOM VALIDATION
# =============================================================================


def validate_bedroom_circulation(

    width,

    height,

    bed_type="queen"
):

    if bed_type == "king":

        bed_w = 6
        bed_h = 6.5

    else:

        bed_w = 5
        bed_h = 6

    required_w = (

        bed_w

        + 2

        + 4
    )

    required_h = (

        bed_h

        + 3
    )

    return (

        width >= required_w

        and

        height >= required_h
    )

# =============================================================================
# ATTACHED BATHROOM
# =============================================================================


def requires_attached_bathroom(

    room_type: str
):

    return room_type in [

        "master_bedroom"
    ]

# =============================================================================
# ENVIRONMENTAL PRIORITY
# =============================================================================


def environmental_priority(

    room_type: str
):

    priorities = {

        "wash_area": 5,

        "kitchen": 5,

        "bathroom": 4,

        "living": 4,

        "bedroom": 3,

        "master_bedroom": 3,

        "dining": 2
    }

    return priorities.get(
        room_type,
        1
    )

# =============================================================================
# WET WALL
# =============================================================================


def requires_wet_wall(

    room_type: str
):

    return room_type in [

        "kitchen",

        "wash_area",

        "bathroom"
    ]

# =============================================================================
# REGION PREFERENCE
# =============================================================================


def room_region_preference(

    room_type: str
):

    return {

        "prefer_exterior":

        requires_exterior_touch(
            room_type
        ),
        
        "prefer_private":

        room_type in [

            "master_bedroom",

            "bedroom"
        ],

        "prefer_service":

        room_type in [

            "kitchen",

            "wash_area",

            "store"
        ]
    }

# =============================================================================
# CLUSTERS
# =============================================================================


def topology_placement_order():

    return [

        # =====================================================
        # ENVIRONMENT
        # =====================================================

        "parking",

        "lawn",

        "staircase",

        # =====================================================
        # SERVICE
        # =====================================================

        "kitchen",

        "wash_area",

        "store",

        # =====================================================
        # PRIVATE
        # =====================================================

        "master_bedroom",

        "bedroom",

        "bathroom",

        # =====================================================
        # SEMI SOCIAL
        # =====================================================

        "dining",

        # =====================================================
        # SOCIAL EMERGENCE
        # =====================================================

        "living"
    ]