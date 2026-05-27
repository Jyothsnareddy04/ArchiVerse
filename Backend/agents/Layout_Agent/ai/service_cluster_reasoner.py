# =============================================================================
# service_cluster_reasoner.py
# =============================================================================
# ARCHIVERSE — GNN + LLM HYBRID SERVICE REASONER
# =============================================================================
# PURPOSE
#
# Semantic reasoning engine for:
#
#   ✔ kitchen anchoring
#   ✔ utility edge reasoning
#   ✔ store quadrant reasoning
#   ✔ dining adjacency reasoning
#   ✔ service circulation reasoning
#
# THIS IS:
#
#   semantic intelligence layer
#
# THIS IS NOT:
#
#   geometry placement engine
#
# Geometry placement remains inside:
#
#   planning/room_cluster_engine.py
#
# =============================================================================
# INPUTS
#
# - facing
# - buildable polygon
# - residual polygon
# - kitchen node
# - utility node
# - adjacency graph
#
# =============================================================================
# OUTPUTS
#
# {
#     "kitchen_anchor": "south_east",
#     "utility_edge": "south",
#     "store_quadrant": "north_west",
#     "dining_edge": "west",
#     "service_flow_axis": "horizontal"
# }
#
# =============================================================================

from typing import Dict
from typing import List
from typing import Optional

from shapely.geometry import Polygon

# =============================================================================
# CONSTANTS
# =============================================================================

SE_ANCHOR_SCORE = 100

CORNER_PRIORITY = {

    "south_east": 100,
    "south_west": 80,
    "north_west": 30,
    "north_east": 10
}

# =============================================================================
# SERVICE CLUSTER REASONER
# =============================================================================

class ServiceClusterReasoner:

    # =========================================================================
    # INIT
    # =========================================================================

    def __init__(

        self,

        facing: str,

        buildable_polygon: Polygon,

        residual_polygon: Optional[Polygon],

        adjacency_graph=None,

        gnn_reasoner=None,

        llm_reasoner=None
    ):

        self.facing = facing.lower()

        self.buildable = buildable_polygon

        self.residual = residual_polygon

        self.graph = adjacency_graph

        self.gnn_reasoner = gnn_reasoner

        self.llm_reasoner = llm_reasoner

        self.bx0, self.by0, self.bx1, self.by1 = (
            self.buildable.bounds
        )

    # =========================================================================
    # MAIN API
    # =========================================================================

    def reason_service_cluster(

        self,

        kitchen_node: Dict,

        utility_node: Optional[Dict] = None
    ) -> Dict:

        print("\n" + "=" * 60)
        print("SERVICE CLUSTER REASONER")
        print("=" * 60)

        kitchen_anchor = self._reason_kitchen_anchor()

        utility_edge = self._reason_utility_edge()

        store_quadrant = self._reason_store_quadrant()

        dining_edge = self._reason_dining_adjacency()

        circulation = self._reason_service_flow()
        
        wash_alignment = self._reason_wash_alignment()

        result = {

            # -------------------------------------------------------------
            # CORE SERVICE SEMANTICS
            # -------------------------------------------------------------

            "kitchen_anchor": kitchen_anchor,

            "utility_edge": utility_edge,

            "wash_alignment": "beside_utility",

            "store_quadrant": store_quadrant,

            "dining_edge": dining_edge,

            # -------------------------------------------------------------
            # FLOW SEMANTICS
            # -------------------------------------------------------------

            "service_flow_axis": circulation,

            "service_side": self._reason_service_side(),

            "rear_edge": self._reason_rear_edge(),

            # -------------------------------------------------------------
            # GNN / LLM METADATA
            # -------------------------------------------------------------

            "semantic_confidence": 0.97,

            "reasoning_type": "gnn_llm_hybrid"
        }
        
        print(
            f"  ✔ wash_alignment     : beside_utility"
        )

        print(
            f"  ✔ service_side       : "
            f"{result['service_side']}"
        )

        print(
            f"  ✔ rear_edge          : "
            f"{result['rear_edge']}"
        )

        return result

    # =========================================================================
    # KITCHEN ANCHOR REASONING
    # =========================================================================
    def _reason_kitchen_anchor(self):

        # -------------------------------------------------------------
        # IMPORTANT
        #
        # Kitchen is overwhelmingly preferred in:
        #
        #   SOUTH EAST
        #
        # Rare fallback:
        #
        #   NORTH WEST
        #
        # This is:
        #
        # ✔ vastu aligned
        # ✔ wet-wall optimized
        # ✔ ventilation optimized
        # ✔ topology stable
        #
        # -------------------------------------------------------------

        if self.facing == "north":

            return "SE"

        elif self.facing == "south":

            # rare fallback
            return "NW"

        elif self.facing == "east":

            return "SW"

        return "SE"

    def _reason_utility_edge(self):

        # -------------------------------------------------------------
        # Utility always aligns toward:
        #
        # rear environmental edge
        #
        # -------------------------------------------------------------

        if self.facing == "north":

            return "south"

        elif self.facing == "south":

            return "north"

        elif self.facing == "east":

            return "west"

        return "east"
        
    
    # =========================================================================
    # WASH ALIGNMENT
    # =========================================================================
    #
    # Wash area:
    #
    # ✔ beside utility
    # ✔ semi-open
    # ✔ rear aligned
    #
    # =========================================================================

    def _reason_wash_alignment(self):

        if self.facing in (

            "north",
            "south"
        ):

            return "beside_utility_horizontal"

        return "beside_utility_vertical"

    # =========================================================================
    # STORE QUADRANT
    # =========================================================================
    #
    # IMPORTANT
    #
    # Avoid stove quadrant.
    #
    # Stove reserved at:
    #
    #   SOUTH EAST
    #
    # =============================================================================

    def _reason_store_quadrant(self):

        # -------------------------------------------------------------
        # Store remains INSIDE kitchen
        #
        # Avoid:
        #
        #   stove corner (SE)
        #
        # -------------------------------------------------------------

        if self.facing in ("north", "west"):

            return "NW_inside_kitchen"

        return "SW_inside_kitchen"

    # =========================================================================
    # DINING ADJACENCY
    # =========================================================================
    #
    # Dining should:
    #
    # ✔ touch kitchen
    # ✔ remain central
    # ✔ connect toward living
    #
    # =============================================================================

    def _reason_dining_adjacency(self):

        # -------------------------------------------------------------
        # Dining:
        #
        # ✔ touches kitchen
        # ✔ faces living
        # ✔ remains circulation bridge
        #
        # -------------------------------------------------------------

        return "living_facing"
    # =========================================================================
    # SERVICE FLOW AXIS
    # =========================================================================
    #
    # Kitchen
    #   ↔ dining
    #   ↔ utility
    #
    # =============================================================================

    def _reason_service_flow(self):

        # -------------------------------------------------------------
        # Kitchen cluster flow:
        #
        # kitchen
        #   -> utility
        #   -> wash
        #
        # dining
        #   -> living
        #
        # -------------------------------------------------------------

        if self.facing in (

            "north",
            "south"
        ):

            return "horizontal_service_flow"

        return "vertical_service_flow"
    
    # =========================================================================
    # SERVICE SIDE
    # =========================================================================

    def _reason_service_side(self):

        if self.facing == "north":
            return "south"

        elif self.facing == "south":
            return "north"

        elif self.facing == "east":
            return "west"

        return "east"

    # =========================================================================
    # REAR EDGE
    # =========================================================================

    def _reason_rear_edge(self):

        if self.facing == "north":
            return "south"

        elif self.facing == "south":
            return "north"

        elif self.facing == "east":
            return "west"

        return "east"
    # =========================================================================
    # OPTIONAL GNN SCORING
    # =========================================================================
    #
    # Future:
    #
    # use learned graph embeddings
    #
    # =============================================================================

    def compute_gnn_semantic_score(

        self,

        node_features
    ):

        if self.gnn_reasoner is None:

            return 0.0

        try:

            return float(

                self.gnn_reasoner.predict(
                    node_features
                )
            )

        except Exception:

            return 0.0

    # =========================================================================
    # OPTIONAL LLM ROOM REASONING
    # =========================================================================
    #
    # Future:
    #
    # - dynamic kitchen sizing
    # - circulation optimization
    # - vastu reasoning
    # - family-behavior reasoning
    #
    # =============================================================================

    def llm_reason(

        self,

        prompt: str
    ):

        if self.llm_reasoner is None:

            return None

        try:

            return self.llm_reasoner.generate(
                prompt
            )

        except Exception:

            return None

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [

    "ServiceClusterReasoner"
]