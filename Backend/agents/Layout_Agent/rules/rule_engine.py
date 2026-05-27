# =============================================================================
# TOPOLOGY-AWARE RULE ENGINE
# =============================================================================
# Production architectural intelligence engine
#
# CORE IDEA:
#
# user input
# → topology intent
# → zoning intent
# → circulation intent
# → environmental intent
# → service intent
# → carving strategy
#
# IMPORTANT:
# This engine does NOT return static standards.
#
# It generates:
# - topology graph
# - room hierarchy
# - environmental openings
# - circulation logic
# - placement priorities
# - adjacency intent
# =============================================================================

from typing import (
    Dict,
    Any,
    List
)

from config.room_standards import (
    ROOM_STANDARDS,
    VASTU_POSITIONS,
    MAIN_DOOR_POSITION,
    MAIN_GATE_POSITION,
    TOPOLOGY_CLUSTERS
)

from rules.room_rules import (
    topology_placement_order,
    room_region_preference,
    get_room_zone,
    required_connections,
    avoid_connections,
    preferred_vastu_position
)

from rules.circulation_rules import (
    circulation_strategy,
    circulation_clusters,
    topology_priority
)

from config.constants import *

# =============================================================================
# MAIN ENGINE
# =============================================================================


def apply_rules(

    requirements: Dict[str, Any],

    facing: str

):

    # =====================================================
    # INPUTS
    # =====================================================

    bedrooms = requirements.get(
        "bedrooms",
        2
    )

    bathrooms = requirements.get(
        "bathrooms",
        1
    )

    optional_rooms = requirements.get(
        "optional_rooms",
        []
    )

    plot_width = requirements.get(
        "plot_width",
        40
    )

    plot_height = requirements.get(
        "plot_height",
        60
    )

    # =====================================================
    # FLAGS
    # =====================================================

    has_backyard = (
        "backyard"
        in
        optional_rooms
    )

    has_store = (
        "store"
        in
        optional_rooms
    )

    has_dining = (
        "dining"
        in
        optional_rooms
    )

    has_parking = requirements.get(
        "parking",
        True
    )

    has_lawn = requirements.get(
        "lawn",
        True
    )

    # =====================================================
    # ROOM LIST
    # =====================================================

    rooms = _build_room_program(

        bedrooms=bedrooms,

        bathrooms=bathrooms,

        has_store=has_store,

        has_dining=has_dining,

        has_backyard=has_backyard,

        has_parking=has_parking,

        has_lawn=has_lawn
    )

    # =====================================================
    # TOPOLOGY ORDER
    # =====================================================

    placement_order = _resolve_order(
        rooms
    )

    # =====================================================
    # CIRCULATION
    # =====================================================

    circulation = circulation_strategy(
        requirements
    )

    # =====================================================
    # ADJACENCY
    # =====================================================

    adjacency = _build_adjacency(
        rooms
    )

    # =====================================================
    # ROOM CONSTRAINTS
    # =====================================================

    room_constraints = _build_constraints(
        rooms
    )

    # =====================================================
    # ENVIRONMENTAL
    # =====================================================

    environmental = _environmental_rules(
        rooms,
        has_backyard
    )

    # =====================================================
    # TOPOLOGY GRAPH
    # =====================================================

    topology_graph = _topology_graph(
        rooms
    )

    # =====================================================
    # OUTPUT
    # =====================================================

    return {

        # =================================================
        # META
        # =================================================

        "facing":
        facing,

        "main_gate":
        MAIN_GATE_POSITION.get(
            facing,
            "north-east"
        ),

        "main_door":
        MAIN_DOOR_POSITION.get(
            facing,
            "north-east"
        ),

        # =================================================
        # PROGRAM
        # =================================================

        "rooms":
        rooms,

        "placement_order":
        placement_order,

        # =================================================
        # TOPOLOGY
        # =================================================

        "adjacency":
        adjacency,

        "topology_graph":
        topology_graph,

        "circulation":
        circulation,

        "topology_priority":
        topology_priority(),

        # =================================================
        # CONSTRAINTS
        # =================================================

        "room_constraints":
        room_constraints,

        "environmental":
        environmental,

        # =================================================
        # STANDARDS
        # =================================================

        "room_standards":
        ROOM_STANDARDS,

        "topology_clusters":
        TOPOLOGY_CLUSTERS,

        "vastu_positions":
        VASTU_POSITIONS
    }

# =============================================================================
# ROOM PROGRAM
# =============================================================================


def _build_room_program(

    bedrooms: int,

    bathrooms: int,

    has_store: bool,

    has_dining: bool,

    has_backyard: bool,

    has_parking: bool,

    has_lawn: bool

):

    rooms = []

    # =====================================================
    # FRONT OPEN
    # =====================================================

    if has_parking:

        rooms.append(
            "parking"
        )

    if has_lawn:

        rooms.append(
            "lawn"
        )

    # =====================================================
    # CORE
    # =====================================================

    rooms.extend([

        "living",

        "kitchen",

        "wash_area",

        "staircase"
    ])

    if has_store:

        rooms.append(
            "store"
        )

    if has_dining:

        rooms.append(
            "dining"
        )

    # =====================================================
    # PRIVATE
    # =====================================================

    if bedrooms >= 1:

        rooms.append(
            "master_bedroom"
        )

    for i in range(
        max(0, bedrooms - 1)
    ):

        rooms.append(
            "bedroom"
        )

    # =====================================================
    # COMMON BATHROOMS
    # =====================================================

    common = max(
        0,
        bathrooms - 1
    )

    for i in range(common):

        rooms.append(
            "bathroom"
        )

    # =====================================================
    # BACKYARD
    # =====================================================

    if has_backyard:

        rooms.append(
            "backyard"
        )

    return rooms

# =============================================================================
# ORDER
# =============================================================================


def _resolve_order(

    rooms: List[str]

):

    order = topology_placement_order()

    resolved = []

    for item in order:

        if item in rooms:

            resolved.append(
                item
            )

    # remaining

    for room in rooms:

        if room not in resolved:

            resolved.append(
                room
            )

    return resolved

# =============================================================================
# ADJACENCY
# =============================================================================


def _build_adjacency(

    rooms: List[str]

):

    adjacency = {}

    for room in rooms:

        adjacency[room] = {

            "must_connect":
            required_connections(room),

            "avoid":
            avoid_connections(room)
        }

    # =====================================================
    # LIVING
    # =====================================================

    if "living" in adjacency:

        adjacency["living"][
            "must_connect"
        ].extend([

            "entrance",

            "parking",

            "lawn"
        ])

    # =====================================================
    # KITCHEN
    # =====================================================

    if "kitchen" in adjacency:

        adjacency["kitchen"][
            "must_connect"
        ].extend([

            "wash_area",

            "store"
        ])

    return adjacency

# =============================================================================
# CONSTRAINTS
# =============================================================================


def _build_constraints(

    rooms: List[str]

):

    constraints = {}

    for room in rooms:

        constraints[room] = {

            "zone":
            get_room_zone(room),

            "vastu":
            preferred_vastu_position(room),

            "preferences":
            room_region_preference(room)
        }

    return constraints

# =============================================================================
# ENVIRONMENT
# =============================================================================


def _environmental_rules(

    rooms: List[str],

    has_backyard: bool

):

    return {

        "cross_ventilation":
        True,

        "service_court":
        has_backyard,

        "wash_exterior":
        "wash_area" in rooms,

        "bathroom_ventilation":
        True,

        "living_front_open":
        True,

        "bedroom_exterior":
        True
    }

# =============================================================================
# TOPOLOGY GRAPH
# =============================================================================


def _topology_graph(

    rooms: List[str]

):

    graph = {

        "social_cluster": [],

        "service_cluster": [],

        "private_cluster": [],

        "environmental_cluster": []
    }

    for room in rooms:

        zone = get_room_zone(
            room
        )

        if zone == "social":

            graph[
                "social_cluster"
            ].append(room)

        elif zone == "service":

            graph[
                "service_cluster"
            ].append(room)

        elif zone == "private":

            graph[
                "private_cluster"
            ].append(room)

        else:

            graph[
                "environmental_cluster"
            ].append(room)

    return graph