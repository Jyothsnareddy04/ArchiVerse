# =============================================================================
# LAYOUT REASONER v2
# =============================================================================
# GNN + LLM SEMANTIC TOPOLOGY REASONER
# =============================================================================
# RESPONSIBILITIES
#
# ✔ facing-aware kitchen preference
# ✔ wet-wall clustering
# ✔ rear-edge reasoning
# ✔ service-side reasoning
# ✔ service circulation generation
# ✔ semantic anchor generation
# ✔ adjacency-aware topology logic
# ✔ multi-facing support
#
# IMPORTANT
#
# This file DOES NOT generate coordinates.
#
# It generates:
#
#   service_edge
#   utility_edge
#   kitchen_anchor
#   wet_wall_axis
#   dining_flow
#   circulation logic
#
# consumed later by:
#
#   service_cluster_reasoner.py
#   room_cluster_engine.py
#   topology_solver.py
#
# =============================================================================

import os
import json
import re

from typing import Dict
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

# =============================================================================
# ENV
# =============================================================================

load_dotenv()

# =============================================================================
# ENGINE
# =============================================================================

class LayoutReasoner:

    # =========================================================================
    # INIT
    # =========================================================================

    def __init__(self):

        self.client = OpenAI(

            api_key=os.getenv(
                "OPENAI_API_KEY"
            )
        )

    # =========================================================================
    # GENERATE TOPOLOGY LOGIC
    # =========================================================================

    def generate_layout_logic(

        self,

        requirements: Dict[str, Any]
    ) -> Dict:

        plot = requirements["plot"]

        facing = requirements["facing"]

        bedrooms = requirements["bedrooms"]

        bathrooms = requirements["bathrooms"]

        optional = requirements.get(
            "optional_rooms",
            []
        )

        plot_width = plot.get("width", 40)
        plot_height = plot.get("height", 60)

        # ---------------------------------------------------------------------
        # PROMPT
        # ---------------------------------------------------------------------

        prompt = f"""
You are an expert Indian residential architect
and semantic topology planner.

Your job is to generate ONLY topology intelligence.

DO NOT generate:
- coordinates
- polygons
- geometry

Generate ONLY:
- semantic anchors
- service edge reasoning
- wet-wall clustering
- circulation logic
- adjacency hierarchy
- room relationship intelligence

# INPUT

Facing:
{facing}

Plot Width:
{plot_width}

Plot Height:
{plot_height}

Bedrooms:
{bedrooms}

Bathrooms:
{bathrooms}

Optional Rooms:
{optional}

# ARCHITECTURAL RULES

VERY IMPORTANT:

1. Kitchen should be:
   - MOSTLY south-east
   - VERY RARELY north-west
   - NEVER center

2. Utility:
   - MUST touch rear/open edge
   - MUST attach kitchen
   - MUST connect backyard/service edge

3. Wash Area:
   - MUST attach utility
   - semi-open
   - near backyard

4. Store:
   - INSIDE kitchen
   - avoid stove corner

5. Dining:
   - MUST touch kitchen
   - SHOULD bridge living
   - SHOULD stay circulation accessible

6. Living:
   - near entrance
   - central circulation anchor

7. Bathrooms:
   - clustered by wet wall logic

8. Stair:
   - side/rear circulation preferred

# REQUIRED OUTPUT

Return STRICT JSON ONLY.

Example structure:

{{
  "topology": {{
    "circulation_type": "central_spine",
    "private_cluster": "rear_split",
    "service_cluster": "south_east"
  }},

  "semantic_anchors": {{
    "service_edge": "south",
    "utility_edge": "rear",
    "kitchen_anchor": "SE",
    "wet_wall_axis": "south",
    "dining_flow": "kitchen_to_living"
  }},

  "service_logic": {{
    "kitchen_preference": "SE",
    "fallback_kitchen": "NW",
    "utility_external": true,
    "store_inside_kitchen": true,
    "wash_near_utility": true
  }},

  "area_distribution": {{
    "social": 32,
    "private": 42,
    "service": 18,
    "circulation": 8
  }},

  "adjacency": {{
    "kitchen": [
      "utility",
      "wash_area",
      "store",
      "dining"
    ],

    "utility": [
      "backyard",
      "wash_area"
    ],

    "dining": [
      "living",
      "kitchen"
    ]
  }},

  "placement_rules": {{
    "kitchen": "south-east",
    "living": "front-connected",
    "master_bedroom": "south-west",

    "utility": "rear_edge_external",
    "wash_area": "utility_attached",
    "store": "inside_kitchen",
    "dining": "living_connected"
  }}
}}
"""

        # ---------------------------------------------------------------------
        # OPENAI
        # ---------------------------------------------------------------------

        try:

            response = self.client.chat.completions.create(

                model="gpt-4.1-mini",

                temperature=0.1,

                messages=[

                    {
                        "role": "system",

                        "content":
                        (
                            "You are a semantic "
                            "architectural topology planner. "
                            "Return STRICT VALID JSON ONLY."
                        )
                    },

                    {
                        "role": "user",

                        "content": prompt
                    }
                ]
            )

            content = response.choices[
                0
            ].message.content.strip()

            parsed = self._parse_json(
                content
            )

            return self._post_process(

                parsed,

                facing
            )

        except Exception as e:

            print(
                f"\n[LLM ERROR] {e}"
            )

            return self._fallback(
                facing
            )

    # =========================================================================
    # POST PROCESS
    # SAFETY NORMALIZATION
    # =========================================================================

    def _post_process(

        self,

        data,

        facing
    ):

        if not isinstance(data, dict):

            return self._fallback(
                facing
            )

        # ---------------------------------------------------------------------
        # ENSURE REQUIRED KEYS
        # ---------------------------------------------------------------------

        if "semantic_anchors" not in data:

            data["semantic_anchors"] = {}

        anchors = data[
            "semantic_anchors"
        ]

        # ---------------------------------------------------------------------
        # FORCE VALID SERVICE EDGES
        # ---------------------------------------------------------------------

        if "service_edge" not in anchors:

            anchors["service_edge"] = (
                self._default_service_edge(
                    facing
                )
            )

        if "utility_edge" not in anchors:

            anchors["utility_edge"] = (
                "rear"
            )

        if "kitchen_anchor" not in anchors:

            anchors["kitchen_anchor"] = (
                self._default_kitchen_anchor(
                    facing
                )
            )

        if "wet_wall_axis" not in anchors:

            anchors["wet_wall_axis"] = (
                anchors["service_edge"]
            )

        if "dining_flow" not in anchors:

            anchors["dining_flow"] = (
                "kitchen_to_living"
            )

        # ---------------------------------------------------------------------
        # ENSURE PLACEMENT RULES
        # ---------------------------------------------------------------------

        if "placement_rules" not in data:

            data["placement_rules"] = {}

        placement = data[
            "placement_rules"
        ]

        placement.setdefault(
            "utility",
            "rear_edge_external"
        )

        placement.setdefault(
            "wash_area",
            "utility_attached"
        )

        placement.setdefault(
            "store",
            "inside_kitchen"
        )

        placement.setdefault(
            "dining",
            "living_connected"
        )
        
        # ---------------------------------------------------------------------
        # PLACEMENT RULES NORMALIZATION
        # ---------------------------------------------------------------------

        if "placement_rules" not in data:

            data["placement_rules"] = {}

        rules = data["placement_rules"]

        # ---------------------------------------------------------------------
        # SERVICE RULES
        # ---------------------------------------------------------------------

        rules.setdefault(

            "utility",

            "rear_edge_external"
        )

        rules.setdefault(

            "wash_area",

            "utility_attached"
        )

        rules.setdefault(

            "store",

            "inside_kitchen"
        )

        rules.setdefault(

            "dining",

            "living_connected"
        )

        # ---------------------------------------------------------------------
        # CORE ROOM RULES
        # ---------------------------------------------------------------------

        rules.setdefault(

            "kitchen",

            anchors["kitchen_anchor"]
        )

        rules.setdefault(

            "living",

            "front-connected"
        )

        rules.setdefault(

            "master_bedroom",

            "south-west"
        )
        

        return data

    # =========================================================================
    # DEFAULT SERVICE EDGE
    # =========================================================================

    def _default_service_edge(

        self,

        facing
    ):

        facing = facing.lower()

        # -------------------------------------------------------------
        # Rear edge reasoning
        # -------------------------------------------------------------

        mapping = {

            "north": "south",

            "south": "north",

            "east": "west",

            "west": "east"
        }

        return mapping.get(
            facing,
            "south"
        )

    # =========================================================================
    # DEFAULT KITCHEN ANCHOR
    # =========================================================================

    def _default_kitchen_anchor(

        self,

        facing
    ):

        facing = facing.lower()

        # -------------------------------------------------------------
        # MOSTLY SOUTH-EAST
        # VERY RARE FALLBACK NW
        # -------------------------------------------------------------

        mapping = {

            "north": "SE",

            "south": "NW",

            "east": "SW",

            "west": "SE"
        }

        return mapping.get(
            facing,
            "SE"
        )

    # =========================================================================
    # JSON PARSER
    # =========================================================================

    def _parse_json(

        self,

        text: str
    ) -> Dict:

        text = re.sub(
            r"```json",
            "",
            text
        )

        text = re.sub(
            r"```",
            "",
            text
        )

        text = text.strip()

        try:

            return json.loads(text)

        except Exception:

            match = re.search(

                r"\{[\s\S]*\}",

                text
            )

            if match:

                try:

                    return json.loads(
                        match.group()
                    )

                except Exception:
                    pass

        return {}

    # =========================================================================
    # FALLBACK
    # =========================================================================

    def _fallback(

        self,

        facing="north"
    ):

        service_edge = (
            self._default_service_edge(
                facing
            )
        )

        kitchen_anchor = (
            self._default_kitchen_anchor(
                facing
            )
        )

        return {

            "topology": {

                "circulation_type":
                "central_spine",

                "private_cluster":
                "rear_split",

                "service_cluster":
                kitchen_anchor
            },

            "semantic_anchors": {

                "service_edge":
                service_edge,

                "utility_edge":
                "rear",

                "kitchen_anchor":
                kitchen_anchor,

                "wet_wall_axis":
                service_edge,

                "dining_flow":
                "kitchen_to_living"
            },

            "service_logic": {

                "kitchen_preference":
                kitchen_anchor,

                "fallback_kitchen":
                "NW",

                "utility_external":
                True,

                "store_inside_kitchen":
                True,

                "wash_near_utility":
                True
            },

            "area_distribution": {

                "social": 32,

                "private": 42,

                "service": 18,

                "circulation": 8
            },

            "adjacency": {

                "kitchen": [

                    "utility",

                    "wash_area",

                    "store",

                    "dining"
                ],

                "utility": [

                    "backyard",

                    "wash_area"
                ],

                "dining": [

                    "living",

                    "kitchen"
                ]
            },

            "placement_rules": {

                # -------------------------------------------------------------
                # SERVICE CLUSTER
                # -------------------------------------------------------------

                "kitchen":
                kitchen_anchor,

                "utility":
                "rear_edge_external",

                "wash_area":
                "utility_attached",

                "store":
                "inside_kitchen",

                "dining":
                "living_connected",

                # -------------------------------------------------------------
                # OTHER ROOMS
                # -------------------------------------------------------------

                "master_bedroom":
                "south-west",

                "living":
                "front-connected"
            }
        }