# =============================================================================
# ARCHIVERSE — TOPOLOGY-AWARE ROOM STANDARDS
# =============================================================================
# Production architectural standards
# for topology-driven residential layout generation.
#
# IMPORTANT:
# Rooms are NOT independent rectangles.
# Rooms belong to:
# - social clusters
# - private clusters
# - service clusters
#
# These standards are used by:
# - topology solver
# - circulation engine
# - region scoring engine
# - geometry refinement engine
# =============================================================================

from .constants import *

# =============================================================================
# ROOM STANDARDS
# =============================================================================

ROOM_STANDARDS = {

    # =========================================================================
    # MASTER BEDROOM
    # =========================================================================

    "master_bedroom": {

        "min_w": MASTER_MIN_W,

        "min_h": MASTER_MIN_H,

        "pref_w": MASTER_PREF_W,

        "pref_h": MASTER_PREF_H,

        "min_area": MASTER_CLUSTER_MIN_AREA,

        "zone": "private",

        "cluster": "private_cluster",

        "requires": [
            "attached_bathroom",
            "wardrobe"
        ],

        "circulation": {

            "side_clearance": 2.0,

            "front_clearance": 2.5
        },

        "placement": {

            "preferred_zone": "south_west",

            "privacy_depth": 2,

            "preferred_exterior_touch": True,

            "near": [
                "attached_bathroom"
            ],

            "away_from": [
                "living",
                "parking"
            ]
        }
    },

    # =========================================================================
    # BEDROOM
    # =========================================================================

    "bedroom": {

        "min_w": BEDROOM_MIN_W,

        "min_h": BEDROOM_MIN_H,

        "pref_w": BEDROOM_PREF_W,

        "pref_h": BEDROOM_PREF_H,

        "min_area": BEDROOM_CLUSTER_MIN_AREA,

        "zone": "private",

        "cluster": "private_cluster",

        "requires": [
            "wardrobe"
        ],

        "circulation": {

            "side_clearance": 2.0,

            "front_clearance": 2.5
        },

        "placement": {

            "privacy_depth": 2,

            "preferred_exterior_touch": True,

            "near": [
                "bathroom"
            ],

            "away_from": [
                "parking",
                "kitchen"
            ]
        }
    },

    # =========================================================================
    # KITCHEN
    # =========================================================================

    "kitchen": {

        "min_w": KITCHEN_MIN_W,

        "min_h": KITCHEN_MIN_H,

        "pref_w": KITCHEN_PREF_W,

        "pref_h": KITCHEN_PREF_H,

        "min_area": SERVICE_CLUSTER_MIN_AREA,

        "zone": "service",

        "cluster": "service_cluster",

        "platform": {

            "shape": "L",

            "length_1": 9.0,

            "length_2": 9.0
        },

        "placement": {

            "preferred_zone":
            KITCHEN_PRIMARY_ZONE,

            "secondary_zone":
            KITCHEN_SECONDARY_ZONE,

            "preferred_exterior_touch": True,

            "near": [
                "wash_area",
                "store",
                "dining"
            ],

            "away_from": [
                "master_bedroom"
            ]
        }
    },

    # =========================================================================
    # WASH AREA
    # =========================================================================

    "wash_area": {

        "min_w": WASH_MIN_W,

        "min_h": WASH_MIN_H,

        "pref_w": WASH_PREF_W,

        "pref_h": WASH_PREF_H,

        "zone": "service",

        "cluster": "service_cluster",

        "placement": {

            "must_attach_to":
            "kitchen",

            "behind_kitchen": True,

            "preferred_exterior_touch": True,

            "environmental_opening_required": True
        }
    },

    # =========================================================================
    # STORE
    # =========================================================================

    "store": {

        "min_w": STORE_MIN_W,

        "min_h": STORE_MIN_H,

        "pref_w": STORE_PREF_W,

        "pref_h": STORE_PREF_H,

        "zone": "service",

        "cluster": "service_cluster",

        "placement": {

            "must_attach_to":
            "kitchen",

            "near": [
                "wash_area"
            ]
        }
    },

    # =========================================================================
    # ATTACHED BATHROOM
    # =========================================================================

    "attached_bathroom": {

        "min_w": BATH_MIN_W,

        "min_h": BATH_MIN_H,

        "pref_w": BATH_PREF_W,

        "pref_h": BATH_PREF_H,

        "min_area":
        ATTACHED_BATH_MIN_AREA,

        "zone": "service",

        "cluster": "private_cluster",

        "placement": {

            "must_attach_to":
            "bedroom",

            "shared_plumbing_wall":
            True,

            "exterior_ventilation":
            True,

            "wet_wall_alignment":
            True
        }
    },

    # =========================================================================
    # COMMON BATHROOM
    # =========================================================================

    "bathroom": {

        "min_w": BATH_MIN_W,

        "min_h": BATH_MIN_H,

        "pref_w": BATH_PREF_W,

        "pref_h": BATH_PREF_H,

        "min_area":
        COMMON_BATH_MIN_AREA,

        "zone": "service",

        "cluster": "service_cluster",

        "placement": {

            "near": [
                "circulation"
            ],

            "away_from": [
                "dining"
            ],

            "exterior_ventilation":
            True
        }
    },

    # =========================================================================
    # LIVING ROOM
    # =========================================================================

    "living": {

        "min_w": LIVING_MIN_W,

        "min_h": LIVING_MIN_H,

        "pref_w": LIVING_PREF_W,

        "pref_h": LIVING_PREF_H,

        "min_area":
        SOCIAL_CLUSTER_MIN_AREA,

        "zone": "social",

        "cluster": "social_cluster",

        "placement": {

            "entrance_connected":
            True,

            "touch_front_open":
            True,

            "near": [
                "dining",
                "staircase"
            ],

            "visual_openness":
            True
        }
    },

    # =========================================================================
    # DINING
    # =========================================================================

    "dining": {

        "min_w": DINING_MIN_W,

        "min_h": DINING_MIN_H,

        "pref_w": DINING_PREF_W,

        "pref_h": DINING_PREF_H,

        "zone": "semi_private",

        "cluster": "social_cluster",

        "placement": {

            "bridge_between": [
                "kitchen",
                "living"
            ],

            "circulation_connected":
            True
        }
    },

    # =========================================================================
    # STAIRCASE
    # =========================================================================

    "staircase": {

        "min_w": STAIR_MIN_W,

        "min_h": STAIR_MIN_H,

        "pref_w": STAIR_PREF_W,

        "pref_h": STAIR_PREF_H,

        "zone": "semi_private",

        "cluster": "circulation_cluster",

        "placement": {

            "valid_zones":
            STAIR_VALID_ZONES,

            "circulation_connected":
            True,

            "may_attach": [
                "backyard",
                "side_court",
                "parking"
            ]
        }
    },

    # =========================================================================
    # PARKING
    # =========================================================================

    "parking": {

        "min_w": PARKING_MIN_W,

        "min_h": PARKING_MIN_H,

        "pref_w": PARKING_PREF_W,

        "pref_h": PARKING_PREF_H,

        "zone": "semi_private",

        "cluster": "front_open_cluster",

        "placement": {

            "front_required":
            True,

            "road_connected":
            True
        }
    },

    # =========================================================================
    # BACKYARD
    # =========================================================================

    "backyard": {

        "min_w": BACKYARD_MIN_W,

        "min_h": BACKYARD_MIN_H,

        "pref_w": BACKYARD_PREF_W,

        "pref_h": BACKYARD_PREF_H,

        "zone": "environmental",

        "cluster": "environmental_cluster",

        "placement": {

            "localized_open_court":
            True,

            "partial_width_allowed":
            True,

            "near": [
                "kitchen",
                "wash_area",
                "bathroom"
            ],

            "environmental_role": [

                "ventilation",
                "utility_drying",
                "light",
                "gardening"
            ]
        }
    },

    # =========================================================================
    # LAWN
    # =========================================================================

    "lawn": {

        "min_w": 8.0,

        "min_h": 5.0,

        "pref_w": 18.0,

        "pref_h": 8.0,

        "zone": "environmental",

        "cluster": "front_open_cluster",

        "placement": {

            "front_required":
            True,

            "living_connected":
            True
        }
    }
}

# =============================================================================
# VASTU + TOPOLOGY
# =============================================================================

VASTU_POSITIONS = {

    "kitchen":
    "south_east",

    "master_bedroom":
    "south_west",

    "living":
    "north_east",

    "bathroom":
    "west",

    "staircase":
    "south_west",

    "dining":
    "center_transition",

    "store":
    "south_east",

    "wash_area":
    "south_east",
}

# =============================================================================
# MAIN GATE
# =============================================================================

MAIN_GATE_POSITION = {

    "east":
    "north_east",

    "north":
    "north_east",

    "west":
    "north_west",

    "south":
    "south_east",
}

# =============================================================================
# MAIN DOOR
# =============================================================================

MAIN_DOOR_POSITION = {

    "east":
    "north_east",

    "north":
    "north_east",

    "west":
    "north_west",

    "south":
    "south_east",
}

# =============================================================================
# STAIRCASE
# =============================================================================

STAIR_VALID_CORNERS = [

    "south_east",

    "north_west",

    "south_west",

    "rear_court"
]

# =============================================================================
# KITCHEN
# =============================================================================

KITCHEN_CORNERS = [

    "south_east",

    "north_west"
]

# =============================================================================
# HOUSE TYPES
# =============================================================================

HOUSE_TYPES = [

    "individual",

    "villa",

    "building"
]

# =============================================================================
# TOPOLOGY CLUSTERS
# =============================================================================

TOPOLOGY_CLUSTERS = {

    "social_cluster": [

        "living",
        "dining"
    ],

    "service_cluster": [

        "kitchen",
        "wash_area",
        "store",
        "bathroom"
    ],

    "private_cluster": [

        "master_bedroom",
        "bedroom",
        "attached_bathroom"
    ],

    "environmental_cluster": [

        "backyard",
        "lawn"
    ]
}