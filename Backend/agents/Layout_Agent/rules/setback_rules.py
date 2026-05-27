# =============================================================================
# TOPOLOGY-AWARE SETBACK RULES
# =============================================================================
# Production setback intelligence engine
#
# IMPORTANT:
# Setbacks are NOT empty leftover strips.
#
# Setbacks become:
# - front circulation topology
# - environmental breathing pockets
# - service courts
# - light shafts
# - ventilation buffers
# - green strips
#
# CORE IDEA:
#
# plot
# → setbacks
# → front topology
# → side environmental strips
# → service pockets
# → buildable core
# =============================================================================

from typing import Dict

from config.ghmc_rules import (
    GHMC,
    SQFT_TO_SQM
)

from config.constants import *

# =============================================================================
# MAIN ENGINE
# =============================================================================


def compute_setbacks(

    plot_area_sqft: float,

    facing: str,

    has_parking: bool = True,

    has_lawn: bool = True,

    has_backyard: bool = False,

    has_plants: bool = False,

    custom_setbacks: Dict = None

):

    # =====================================================
    # AREA
    # =====================================================

    area_sqm = (
        plot_area_sqft
        * SQFT_TO_SQM
    )

    # =====================================================
    # CUSTOM
    # =====================================================

    if custom_setbacks:

        return _normalize_custom(
            custom_setbacks
        )

    # =====================================================
    # GHMC
    # =====================================================

    setbacks = GHMC.setbacks(

        plot_area_sqm=area_sqm,

        facing=facing,

        has_parking=has_parking,

        has_lawn=has_lawn,

        has_backyard=has_backyard,

        has_plants=has_plants
    )

    # =====================================================
    # FRONT TOPOLOGY OVERRIDE
    # =====================================================

    setbacks = _apply_front_topology(

        setbacks,

        facing,

        has_parking,

        has_lawn
    )

    # =====================================================
    # SIDE GREEN STRIPS
    # =====================================================

    setbacks = _apply_green_strips(

        setbacks,

        facing,

        has_plants
    )

    # =====================================================
    # SERVICE COURT
    # =====================================================

    setbacks = _apply_service_logic(

        setbacks,

        facing,

        has_backyard
    )

    return setbacks

# =============================================================================
# FRONT TOPOLOGY
# =============================================================================


def _apply_front_topology(

    setbacks: Dict,

    facing: str,

    has_parking: bool,

    has_lawn: bool

):

    """
    IMPORTANT:
    Front setback should NOT consume:
    parking + lawn topology.
    """

    front_depth = 0

    if has_parking:

        front_depth += PARKING_PREF_H

    if has_lawn:

        front_depth += LAWN_MIN_DEPTH

    # =====================================================
    # MINIMUM FRONT OPEN
    # =====================================================

    front_depth = max(

        front_depth,

        MIN_FRONT_OPEN
    )

    setbacks[facing] = front_depth

    return setbacks

# =============================================================================
# GREEN STRIPS
# =============================================================================


def _apply_green_strips(

    setbacks: Dict,

    facing: str,

    has_plants: bool

):

    """
    Side environmental breathing strips.
    """

    if not has_plants:

        return setbacks

    # =====================================================
    # SIDES
    # =====================================================

    if facing in ["north", "south"]:

        setbacks["east"] += PLANT_STRIP

        setbacks["west"] += PLANT_STRIP

    else:

        setbacks["north"] += PLANT_STRIP

        setbacks["south"] += PLANT_STRIP

    return setbacks

# =============================================================================
# SERVICE COURT
# =============================================================================


def _apply_service_logic(

    setbacks: Dict,

    facing: str,

    has_backyard: bool

):

    """
    Backyard becomes:
    utility + ventilation + drying court.
    """

    if not has_backyard:

        return setbacks

    opposite = {

        "north": "south",

        "south": "north",

        "east": "west",

        "west": "east"
    }

    rear = opposite[facing]

    setbacks[rear] = max(

        setbacks[rear],

        BACKYARD_PREF_H
    )

    return setbacks

# =============================================================================
# CUSTOM
# =============================================================================


def _normalize_custom(

    setbacks: Dict

):

    result = {

        "north":
        float(setbacks.get("north", 0)),

        "south":
        float(setbacks.get("south", 0)),

        "east":
        float(setbacks.get("east", 0)),

        "west":
        float(setbacks.get("west", 0))
    }

    return result

# =============================================================================
# BUILDABLE AREA
# =============================================================================


def compute_buildable_area(

    plot_width: float,

    plot_height: float,

    setbacks: Dict

):

    width = (

        plot_width

        - setbacks["east"]

        - setbacks["west"]
    )

    height = (

        plot_height

        - setbacks["north"]

        - setbacks["south"]
    )

    return max(width, 0), max(height, 0)

# =============================================================================
# FRONT OPEN SIDE
# =============================================================================


def front_open_side(

    facing: str

):

    return facing

# =============================================================================
# REAR SIDE
# =============================================================================


def rear_side(

    facing: str

):

    mapping = {

        "north": "south",

        "south": "north",

        "east": "west",

        "west": "east"
    }

    return mapping[facing]

# =============================================================================
# SIDE EDGES
# =============================================================================


def side_edges(

    facing: str

):

    if facing in ["north", "south"]:

        return ["east", "west"]

    return ["north", "south"]

# =============================================================================
# FRONT OPEN DEPTH
# =============================================================================


def front_open_depth(

    has_parking: bool = True,

    has_lawn: bool = True

):

    depth = 0

    if has_parking:

        depth += PARKING_PREF_H

    if has_lawn:

        depth += LAWN_MIN_DEPTH

    return max(

        depth,

        MIN_FRONT_OPEN
    )

# =============================================================================
# ENVIRONMENTAL OPENINGS
# =============================================================================


def environmental_openings(

    has_backyard: bool,

    has_plants: bool

):

    return {

        "service_court":
        has_backyard,

        "green_strips":
        has_plants,

        "cross_ventilation":
        True,

        "light_pockets":
        True
    }

# =============================================================================
# SETBACK REPORT
# =============================================================================


def setback_summary(

    setbacks: Dict

):

    total = sum(
        setbacks.values()
    )

    return {

        "north":
        round(setbacks["north"], 2),

        "south":
        round(setbacks["south"], 2),

        "east":
        round(setbacks["east"], 2),

        "west":
        round(setbacks["west"], 2),

        "total":
        round(total, 2)
    }