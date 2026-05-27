# =============================================================================
# TOPOLOGY-AWARE STRUCTURAL RULES
# =============================================================================
# Production structural intelligence
#
# IMPORTANT:
# Structure is NOT just wall thickness.
#
# Structure controls:
# - wall hierarchy
# - wet wall alignment
# - structural continuity
# - room span feasibility
# - circulation feasibility
# - load distribution intent
# - column-safe topology
# =============================================================================

from typing import Dict

from config.constants import *

# =============================================================================
# WALL THICKNESS
# =============================================================================


def wall_offset(

    is_exterior: bool = False

):

    return (

        OUTER_WALL

        if is_exterior

        else INNER_WALL
    )

# =============================================================================
# WALL TYPES
# =============================================================================


def wall_types():

    return {

        "outer_wall":
        OUTER_WALL,

        "inner_wall":
        INNER_WALL,

        "stair_wall":
        STAIR_WALL
    }

# =============================================================================
# ROOM SPAN LIMITS
# =============================================================================


def max_room_span(

    room_type: str

):

    """
    Structural span feasibility.
    """

    spans = {

        "living": 22,

        "dining": 16,

        "master_bedroom": 16,

        "bedroom": 14,

        "kitchen": 12,

        "bathroom": 8,

        "wash_area": 8
    }

    return spans.get(
        room_type,
        12
    )

# =============================================================================
# MINIMUM ROOM SPAN
# =============================================================================


def minimum_room_span(

    room_type: str

):

    minimums = {

        "living": 10,

        "dining": 9,

        "master_bedroom": 12,

        "bedroom": 10,

        "kitchen": 9,

        "bathroom": 4
    }

    return minimums.get(
        room_type,
        6
    )

# =============================================================================
# WET WALL
# =============================================================================


def wet_wall_required(

    room_type: str

):

    return room_type in [

        "kitchen",

        "bathroom",

        "wash_area",

        "attached_bathroom"
    ]

# =============================================================================
# WET WALL GROUPING
# =============================================================================


def structural_grouping():

    """
    Structural service grouping.
    """

    return {

        "wet_cluster": [

            "kitchen",

            "wash_area",

            "bathroom",

            "attached_bathroom"
        ],

        "dry_cluster": [

            "living",

            "dining",

            "bedroom",

            "master_bedroom"
        ]
    }

# =============================================================================
# LOAD PRIORITY
# =============================================================================


def load_priority(

    room_type: str

):

    """
    Higher value → stronger structural continuity preferred.
    """

    priority = {

        "staircase": 5,

        "bathroom": 4,

        "attached_bathroom": 4,

        "kitchen": 4,

        "living": 3,

        "master_bedroom": 3,

        "bedroom": 2,

        "wash_area": 2
    }

    return priority.get(
        room_type,
        1
    )

# =============================================================================
# COLUMN GRID
# =============================================================================


def preferred_column_spacing():

    """
    Standard RCC residential spacing.
    """

    return {

        "min": 10,

        "preferred": 12,

        "max": 16
    }

# =============================================================================
# STAIRCASE
# =============================================================================


def staircase_structural_rules():

    return {

        "min_width":
        STAIR_TOTAL_W,

        "preferred_width":
        STAIR_PREF_W,

        "wall_thickness":
        STAIR_WALL,

        "valid_zones":
        STAIR_VALID_ZONES
    }

# =============================================================================
# WALL ALIGNMENT
# =============================================================================


def wall_alignment_priority():

    """
    Priority for aligned walls.
    """

    return {

        "wet_wall_alignment":
        True,

        "exterior_wall_alignment":
        True,

        "circulation_alignment":
        True,

        "structural_grid_alignment":
        True
    }

# =============================================================================
# CANTILEVER CONTROL
# =============================================================================


def cantilever_rules():

    return {

        "max_projection": 4,

        "avoid_irregular_projection":
        True,

        "prefer_flush_edges":
        True
    }

# =============================================================================
# STRUCTURAL FEASIBILITY
# =============================================================================


def validate_structural_span(

    room_type: str,

    width: float,

    height: float

):

    max_span = max_room_span(
        room_type
    )

    if width > max_span:

        return False

    if height > max_span:

        return False

    return True

# =============================================================================
# WALL HIERARCHY
# =============================================================================


def wall_hierarchy():

    return {

        "primary":
        OUTER_WALL,

        "secondary":
        INNER_WALL,

        "service":
        INNER_WALL,

        "stair":
        STAIR_WALL
    }

# =============================================================================
# STRUCTURAL TOPOLOGY
# =============================================================================


def structural_topology_rules():

    """
    Structural layout intent.
    """

    return {

        "prefer_compact_mass":
        True,

        "avoid_fragmentation":
        True,

        "wet_zones_clustered":
        True,

        "staircase_structural_anchor":
        True,

        "minimize_dead_corners":
        True,

        "prefer_aligned_walls":
        True
    }

# =============================================================================
# STRUCTURAL SCORE
# =============================================================================


def structural_score(

    room_type: str,

    width: float,

    height: float

):

    score = 100

    max_span = max_room_span(
        room_type
    )

    span = max(width, height)

    if span > max_span:

        overflow = span - max_span

        score -= overflow * 10

    ratio = max(width, height) / max(
        min(width, height),
        1
    )

    if ratio > 3:

        score -= 15

    return max(
        round(score, 2),
        0
    )