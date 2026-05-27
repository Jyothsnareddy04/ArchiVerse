# =============================================================================
# TOPOLOGY ADJACENCY PLANNER v13
# =============================================================================
# GNN + ARCHITECTURAL SEMANTIC ADJACENCY GRAPH
# =============================================================================
# FIXES
#
# ✔ kitchen ↔ dining strong
# ✔ kitchen ↔ utility mandatory
# ✔ utility ↔ backyard mandatory
# ✔ store ↔ kitchen containment
# ✔ dining ↔ living preferred
# ✔ semantic service cluster hierarchy
# ✔ architectural circulation flow
# ✔ GNN-compatible edge reasoning
# ✔ topology-safe connectivity
# ✔ removes insane mesh explosion
#
# =============================================================================
#
# THIS FILE NOW REPRESENTS:
#
#   SEMANTIC RELATIONSHIP GRAPH
#
# used by:
#
#   topology solver
#   room cluster engine
#   GNN topology reasoning
#   circulation intelligence
#
# =============================================================================

from typing import Dict
from typing import List

# =============================================================================
# HELPERS
# =============================================================================

def add_pair(

    graph,

    a,

    b,

    weight,

    reason,

    mandatory=False
):

    if a == b:
        return

    key = tuple(
        sorted([a, b])
    )

    if key not in graph:

        graph[key] = {

            "weight": weight,

            "mandatory": mandatory,

            "reasons": [reason]
        }

    else:

        graph[key]["weight"] += weight

        graph[key]["mandatory"] = (

            graph[key]["mandatory"]
            or
            mandatory
        )

        if reason not in graph[key]["reasons"]:

            graph[key]["reasons"].append(
                reason
            )

# =============================================================================
# BUILD GRAPH
# =============================================================================

def build_adjacency_graph(

    gnn_zones: Dict,

    llm_plan: Dict,

    room_names: List[str]
):

    graph = {}

    # =========================================================================
    # ROOM TYPE EXTRACTION
    # =========================================================================

    bedrooms = [

        r for r in room_names

        if (
            "bedroom" in r
            and
            "bathroom" not in r
        )
    ]

    bathrooms = [

        r for r in room_names

        if "bathroom" in r
    ]

    kitchens = [

        r for r in room_names

        if "kitchen" in r
    ]

    utilities = [

        r for r in room_names

        if "utility" in r
    ]

    wash_areas = [

        r for r in room_names

        if "wash" in r
    ]

    stores = [

        r for r in room_names

        if "store" in r
    ]

    dining_rooms = [

        r for r in room_names

        if "dining" in r
    ]

    living_rooms = [

        r for r in room_names

        if "living" in r
    ]

    staircases = [

        r for r in room_names

        if "stair" in r
    ]

    parking_rooms = [

        r for r in room_names

        if "parking" in r
    ]

    backyards = [

        r for r in room_names

        if "backyard" in r
    ]

    green_strips = [

        r for r in room_names

        if "green_strip" in r
    ]

    # =========================================================================
    # LLM ADJACENCY
    # =========================================================================

    llm_adj = llm_plan.get(
        "adjacency",
        {}
    )

    for room, neighbors in llm_adj.items():

        if room not in room_names:
            continue

        for nb in neighbors:

            if nb not in room_names:
                continue

            add_pair(

                graph,

                room,

                nb,

                weight=8,

                reason="llm_semantic"
            )

    # =========================================================================
    # GNN ZONE BOOSTING
    # =========================================================================

    # -------------------------------------------------------------------------
    # SERVICE CLUSTER
    # -------------------------------------------------------------------------

    for kitchen in kitchens:

        # -------------------------------------------------------------
        # kitchen ↔ utility
        # MANDATORY
        # -------------------------------------------------------------

        for utility in utilities:

            add_pair(

                graph,

                kitchen,

                utility,

                weight=50,

                reason="kitchen_utility",

                mandatory=True
            )

        # -------------------------------------------------------------
        # kitchen ↔ store
        # containment semantic
        # -------------------------------------------------------------

        for store in stores:

            add_pair(

                graph,

                kitchen,

                store,

                weight=42,

                reason="kitchen_store_containment",

                mandatory=True
            )

        # -------------------------------------------------------------
        # kitchen ↔ wash
        # -------------------------------------------------------------

        for wash in wash_areas:

            add_pair(

                graph,

                kitchen,

                wash,

                weight=36,

                reason="kitchen_wash"
            )

        # -------------------------------------------------------------
        # kitchen ↔ dining
        # strongest social-service edge
        # -------------------------------------------------------------

        for dining in dining_rooms:

            add_pair(

                graph,

                kitchen,

                dining,

                weight=48,

                reason="kitchen_dining",

                mandatory=True
            )

    # =========================================================================
    # UTILITY ↔ BACKYARD
    # =========================================================================

    for utility in utilities:

        for backyard in backyards:

            add_pair(

                graph,

                utility,

                backyard,

                weight=52,

                reason="utility_rear_access",

                mandatory=True
            )

    # =========================================================================
    # WASH ↔ UTILITY
    # =========================================================================

    for wash in wash_areas:

        for utility in utilities:

            add_pair(

                graph,

                wash,

                utility,

                weight=34,

                reason="wash_utility"
            )

    # =========================================================================
    # DINING ↔ LIVING
    # =========================================================================

    for dining in dining_rooms:

        for living in living_rooms:

            add_pair(

                graph,

                dining,

                living,

                weight=38,

                reason="social_flow",

                mandatory=True
            )

    # =========================================================================
    # BEDROOM ↔ LIVING
    # =========================================================================

    for bedroom in bedrooms:

        for living in living_rooms:

            add_pair(

                graph,

                bedroom,

                living,

                weight=16,

                reason="private_to_social"
            )

    # =========================================================================
    # ATTACHED BATHROOMS
    # =========================================================================

    attached_count = min(

        len(bedrooms),

        len(bathrooms)
    )

    for i in range(attached_count):

        add_pair(

            graph,

            bedrooms[i],

            bathrooms[i],

            weight=44,

            reason="attached_bathroom",

            mandatory=True
        )

    # =========================================================================
    # COMMON BATHROOM
    # =========================================================================

    if len(bathrooms) > attached_count:

        common_bath = bathrooms[-1]

        for living in living_rooms:

            add_pair(

                graph,

                living,

                common_bath,

                weight=16,

                reason="common_bathroom"
            )

    # =========================================================================
    # STAIR CONNECTIVITY
    # =========================================================================

    for stair in staircases:

        for living in living_rooms:

            add_pair(

                graph,

                stair,

                living,

                weight=22,

                reason="vertical_circulation"
            )

        for parking in parking_rooms:

            add_pair(

                graph,

                stair,

                parking,

                weight=20,

                reason="entry_connection"
            )

    # =========================================================================
    # GREEN / ENVIRONMENTAL FLOW
    # =========================================================================

    for backyard in backyards:

        for green in green_strips:

            add_pair(

                graph,

                backyard,

                green,

                weight=18,

                reason="environmental_continuity"
            )

    # =========================================================================
    # REMOVE INSANE MESH EXPLOSION
    # =========================================================================
    #
    # DO NOT:
    #
    # bathroom ↔ bathroom
    # bedroom ↔ bedroom
    # utility ↔ all rooms
    #
    # =============================================================================

    # =========================================================================
    # FINAL GRAPH
    # =========================================================================

    adjacency_pairs = []

    print("\n" + "=" * 70)
    print("SEMANTIC TOPOLOGY ADJACENCY GRAPH")
    print("=" * 70)

    sorted_graph = sorted(

        graph.items(),

        key=lambda x: x[1]["weight"],

        reverse=True
    )

    for pair, meta in sorted_graph:

        adjacency_pairs.append(pair)

        mandatory = (
            "MANDATORY"
            if meta["mandatory"]
            else "OPTIONAL"
        )

        print(

            f"  {pair[0]:20s}"

            f"{pair[1]:20s}"

            f"W={meta['weight']:3d}"

            f"  {mandatory:10s}"

            f"  {meta['reasons']}"
        )

    return adjacency_pairs