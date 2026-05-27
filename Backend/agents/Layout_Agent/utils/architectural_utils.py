# =============================================================================
# ARCHITECTURAL UTILITIES v6
# =============================================================================
# Semantic topology architectural utilities
#
# RESPONSIBILITIES
#
# - room sizing
# - topology feasibility
# - buildable estimation
# - topology allocation
# - architectural reporting
#
# DOES NOT:
#
# - generate geometry
# - mutate topology
# - create placements
# - force adjacency
# =============================================================================

from typing import Dict
from typing import Any
from typing import List

from config.room_standards import (
    ROOM_STANDARDS
)

# =============================================================================
# BHK LABEL
# =============================================================================

def get_bhk_label(

    bedrooms: int
):

    return f"{bedrooms}BHK"

# =============================================================================
# ROOM AREA
# =============================================================================

def room_area(

    room_type: str,

    preferred=True
):

    std = ROOM_STANDARDS.get(

        room_type,

        {
            "pref_w": 8,
            "pref_h": 8,

            "min_w": 5,
            "min_h": 5
        }
    )

    if preferred:

        return (

            std["pref_w"]

            * std["pref_h"]
        )

    return (

        std["min_w"]

        * std["min_h"]
    )

# =============================================================================
# ROOM DIMENSIONS
# =============================================================================

def room_dimensions(

    room_type: str,

    preferred=True
):

    std = ROOM_STANDARDS.get(

        room_type,

        {
            "pref_w": 8,
            "pref_h": 8,

            "min_w": 5,
            "min_h": 5
        }
    )

    if preferred:

        return (

            std["pref_w"],

            std["pref_h"]
        )

    return (

        std["min_w"],

        std["min_h"]
    )

# =============================================================================
# ROOM PROGRAM
# =============================================================================

def estimate_room_program(

    bedrooms: int,

    bathrooms: int,

    optional_rooms: List[str]
):

    rooms = []

    # =============================================================
    # SOCIAL
    # =============================================================

    rooms.append({

        "name": "living",

        "type": "living"
    })

    rooms.append({

        "name": "dining",

        "type": "dining"
    })

    # =============================================================
    # SERVICE
    # =============================================================

    rooms.append({

        "name": "kitchen",

        "type": "kitchen"
    })

    rooms.append({

        "name": "wash_area",

        "type": "wash_area"
    })

    if "store" in optional_rooms:

        rooms.append({

            "name": "store",

            "type": "store"
        })

    # =============================================================
    # PRIVATE
    # =============================================================

    rooms.append({

        "name": "master_bedroom",

        "type": "master_bedroom"
    })

    for i in range(max(0, bedrooms - 1)):

        rooms.append({

            "name": f"bedroom_{i+1}",

            "type": "bedroom"
        })

    # =============================================================
    # BATHROOMS
    # =============================================================

    for i in range(bathrooms):

        rooms.append({

            "name": f"bathroom_{i+1}",

            "type": "bathroom"
        })

    return rooms

# =============================================================================
# AREA ESTIMATION
# =============================================================================

def estimate_required_area(

    bedrooms: int,

    bathrooms: int,

    optional_rooms: List[str]
):

    total = 0.0

    rooms = estimate_room_program(

        bedrooms,

        bathrooms,

        optional_rooms
    )

    # =============================================================
    # ROOM AREAS
    # =============================================================

    for room in rooms:

        total += room_area(

            room["type"],

            preferred=True
        )

    # =============================================================
    # CIRCULATION
    # =============================================================

    circulation_factor = 0.12

    total += total * circulation_factor

    # =============================================================
    # WALLS
    # =============================================================

    wall_factor = 0.08

    total += total * wall_factor

    # =============================================================
    # ENVIRONMENTAL
    # =============================================================

    environmental_factor = 0.05

    total += total * environmental_factor

    return round(total, 2)

# =============================================================================
# FEASIBILITY
# =============================================================================

def check_plot_feasibility(

    plot_width: float,

    plot_height: float,

    required_area: float
):

    plot_area = (

        plot_width

        * plot_height
    )

    usable_factor = 0.68

    usable_area = (

        plot_area

        * usable_factor
    )

    feasible = usable_area >= required_area

    return {

        "plot_area":
        round(plot_area, 2),

        "usable_area":
        round(usable_area, 2),

        "required_area":
        round(required_area, 2),

        "feasible":
        feasible,

        "surplus":
        round(

            usable_area - required_area,

            2
        )
    }

# =============================================================================
# TOPOLOGY SPLIT
# =============================================================================

def topology_split_percentages(

    bedrooms: int
):

    private_percent = min(

        42,

        24 + (bedrooms * 5)
    )

    service_percent = 16

    social_percent = 28

    remaining = (

        100

        - private_percent

        - service_percent

        - social_percent
    )

    return {

        "private":
        private_percent,

        "service":
        service_percent,

        "social":
        social_percent,

        "semi_private":
        remaining
    }

# =============================================================================
# DYNAMIC ROOM SIZES
# =============================================================================

def generate_dynamic_room_sizes(

    buildable_area: float,

    bedrooms: int,

    bathrooms: int
):

    splits = topology_split_percentages(
        bedrooms
    )

    social_area = (

        buildable_area

        * splits["social"]

    ) / 100

    room_sizes = {

        # =========================================================
        # SOCIAL
        # =========================================================

        "living": {

            "width": 18,

            "height": max(

                13,

                social_area / 18
            )
        },

        "dining": {

            "width": 11,

            "height": 10
        },

        # =========================================================
        # SERVICE
        # =========================================================

        "kitchen": {

            "width": 11,

            "height": 10
        },

        "wash_area": {

            "width": 7,

            "height": 5
        },

        "store": {

            "width": 5,

            "height": 5
        },

        # =========================================================
        # PRIVATE
        # =========================================================

        "master_bedroom": {

            "width": 14,

            "height": 14
        },

        "bedroom": {

            "width": 12,

            "height": 12
        },

        "bathroom": {

            "width": 5,

            "height": 7
        }
    }

    return room_sizes

# =============================================================================
# TOPOLOGY REPORT
# =============================================================================

def generate_topology_report(

    requirements: Dict[str, Any]
):

    bedrooms = requirements.get(
        "bedrooms",
        2
    )

    bathrooms = requirements.get(
        "bathrooms",
        2
    )

    optional_rooms = requirements.get(
        "optional_rooms",
        []
    )

    plot = requirements.get(
        "plot",
        (40, 60)
    )

    plot_area = plot[0] * plot[1]

    required = estimate_required_area(

        bedrooms,

        bathrooms,

        optional_rooms
    )

    feasibility = check_plot_feasibility(

        plot[0],

        plot[1],

        required
    )

    topology = topology_split_percentages(
        bedrooms
    )

    return {

        "bhk":
        get_bhk_label(bedrooms),

        "plot_area":
        plot_area,

        "required_area":
        required,

        "feasible":
        feasibility,

        "topology_split":
        topology
    }