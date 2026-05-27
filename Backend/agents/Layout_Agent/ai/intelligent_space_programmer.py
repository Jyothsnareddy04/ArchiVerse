# =============================================================================
# intelligent_space_programmer.py
# =============================================================================
# ARCHIVERSE — DIMENSIONAL INTELLIGENCE LAYER v31
# =============================================================================
# PURPOSE
#
# THIS FILE DOES:
#
# ✔ ergonomic dimensional intelligence
# ✔ room sizing refinement
# ✔ aspect-ratio intelligence
# ✔ circulation clearance refinement
# ✔ semantic room scaling
# ✔ topology-aware dimensional balancing
# ✔ service cluster dimensional tuning
# ✔ LLM-assisted sizing refinement
#
# THIS FILE DOES NOT:
#
# ✘ geometry placement
# ✘ topology placement
# ✘ polygon creation
# ✘ room anchoring
#
# =============================================================================
#
# PIPELINE ROLE
#
# LLM
#   ↓
# dimensional refinement
#   ↓
# topology solver
#   ↓
# geometry placement
#
# =============================================================================

from math import sqrt
import random
import os
import json
import re

from dotenv import load_dotenv
from openai import OpenAI

# =============================================================================
# ENV
# =============================================================================

load_dotenv()

# =============================================================================
# CONSTANTS
# =============================================================================

TARGET_UTILIZATION = 0.72

MIN_ROOM_AREA = 25.0
MAX_ROOM_AREA = 340.0

MIN_DIMENSION = 5.0
MAX_DIMENSION = 24.0

ROOM_VARIATION_FACTOR = 0.12

# =============================================================================
# SEMANTIC ROOM RULES
# =============================================================================

ROOM_RULES = {

    # =========================================================================
    # SOCIAL
    # =========================================================================

    "living": {

        "min": 180,
        "ideal": 250,
        "max": 340,

        "priority": 10,

        "aspect": (1.0, 1.8),

        "preferred_width": (14, 18),
        "preferred_depth": (14, 20),

        "clearance": 4.0
    },

    "dining": {

        "min": 80,
        "ideal": 120,
        "max": 180,

        "priority": 8,

        "aspect": (1.0, 1.8),

        "preferred_width": (9, 13),
        "preferred_depth": (8, 12),

        "clearance": 3.0
    },

    # =========================================================================
    # PRIVATE
    # =========================================================================

    "master_bedroom": {

        "min": 130,
        "ideal": 180,
        "max": 240,

        "priority": 9,

        "aspect": (0.9, 1.5),

        "preferred_width": (11, 15),
        "preferred_depth": (11, 16),

        "clearance": 3.0
    },

    "bedroom": {

        "min": 100,
        "ideal": 135,
        "max": 180,

        "priority": 8,

        "aspect": (0.9, 1.5),

        "preferred_width": (10, 13),
        "preferred_depth": (10, 14),

        "clearance": 3.0
    },

    # =========================================================================
    # SERVICE
    # =========================================================================

    "kitchen": {

        "min": 90,
        "ideal": 125,
        "max": 180,

        "priority": 8,

        "aspect": (1.1, 1.6),

        "preferred_width": (10, 13),
        "preferred_height": (8, 11)
    },

    "utility": {

        "min": 30,
        "ideal": 45,
        "max": 70,

        "priority": 5,

        "aspect": (0.7, 1.3),

        "preferred_width": (4, 6),
        "preferred_height": (6, 9)
    },

    "wash_area": {

        "min": 20,
        "ideal": 30,
        "max": 45,

        "priority": 5,

        "aspect": (0.7, 1.5),

        # -------------------------------------------------------------
        # SEMANTIC ERGONOMIC DIMENSIONS
        # -------------------------------------------------------------

        "preferred_width": (4, 5),
        "preferred_height": (5, 7),

        # backward compatibility
        "preferred_depth": (5, 7),

        "clearance": 2.0
    },

    "store": {

        "min": 20,
        "ideal": 25,
        "max": 30,

        "priority": 4,

        # -------------------------------------------------------------
        # REQUIRED FOR PIPELINE COMPATIBILITY
        # -------------------------------------------------------------

        "aspect": (0.8, 1.3),

        # -------------------------------------------------------------
        # FIXED ERGONOMIC DIMENSIONS
        # -------------------------------------------------------------

        "fixed_width": 4,
        "fixed_height": 5,

        "inside_kitchen": True
    },

    # =========================================================================
    # BATHROOM
    # =========================================================================

    "bathroom": {

        "min": 25,
        "ideal": 40,
        "max": 60,

        "priority": 6,

        "aspect": (0.7, 1.4),

        "preferred_width": (5, 7),
        "preferred_depth": (5, 8),

        "clearance": 2.0
    }
}

# =============================================================================
# ENGINE
# =============================================================================

class IntelligentSpaceProgrammer:

    # =========================================================================
    # INIT
    # =========================================================================

    def __init__(

        self,

        state
    ):

        self.state = state

        self.client = OpenAI(

            api_key=os.getenv(
                "OPENAI_API_KEY"
            )
        )

    # =========================================================================
    # MAIN
    # =========================================================================

    def generate_program(

        self,

        rooms
    ):

        if not rooms:
            return []

        usable_area = self._compute_usable_area()

        target_budget = (
            usable_area
            *
            TARGET_UTILIZATION
        )

        programs = []

        # ---------------------------------------------------------------------
        # BUILD PROGRAM
        # ---------------------------------------------------------------------

        for room in rooms:

            room_type = room.get(
                "type",
                "bedroom"
            )

            rules = ROOM_RULES.get(

                room_type,

                ROOM_RULES["bedroom"]
            )

            programs.append({

                "name": room.get(
                    "name",
                    room_type
                ),

                "type": room_type,

                "priority": rules["priority"],

                "rules": rules
            })

        # ---------------------------------------------------------------------
        # SORT
        # ---------------------------------------------------------------------

        programs.sort(

            key=lambda x: x["priority"],

            reverse=True
        )

        # ---------------------------------------------------------------------
        # IDEAL TOTAL
        # ---------------------------------------------------------------------

        total_ideal = sum(

            p["rules"]["ideal"]

            for p in programs
        )

        total_ideal = max(
            total_ideal,
            1.0
        )

        scale = min(

            1.0,

            target_budget / total_ideal
        )

        normalized = []

        # ---------------------------------------------------------------------
        # GENERATE DIMENSIONS
        # ---------------------------------------------------------------------

        for room in programs:

            rules = room["rules"]

            room_type = room["type"]

            # -------------------------------------------------------------
            # AREA
            # -------------------------------------------------------------

            area = (
                rules["ideal"]
                *
                scale
            )

            area = max(

                rules["min"],

                min(
                    area,
                    rules["max"]
                )
            )

            # -------------------------------------------------------------
            # NATURAL VARIATION
            # -------------------------------------------------------------

            area *= random.uniform(

                1.0 - ROOM_VARIATION_FACTOR,

                1.0 + ROOM_VARIATION_FACTOR
            )
            
            rules = ROOM_RULES.get(

                room_type,

                ROOM_RULES["bedroom"]
            ).copy()

            # =========================================================
            # DYNAMIC DIMENSIONAL INTELLIGENCE
            # =========================================================

            rules = self._dynamic_room_bias(

                room_type,

                rules
            )

            # -------------------------------------------------------------
            # CLAMP
            # -------------------------------------------------------------

            area = max(
                MIN_ROOM_AREA,
                min(
                    area,
                    MAX_ROOM_AREA
                )
            )

            # -------------------------------------------------------------
            # DIMENSIONAL INTELLIGENCE
            # -------------------------------------------------------------

            width, height = (

                self._derive_dimensions(

                    room_type,

                    area,

                    rules
                )
            )

            # -------------------------------------------------------------
            # LLM REFINEMENT
            # -------------------------------------------------------------

            width, height = (

                self._llm_refine_dimensions(

                    room_type,

                    width,

                    height,

                    area
                )
            )

            # -------------------------------------------------------------
            # FINAL AREA
            # -------------------------------------------------------------

            final_area = (
                width
                *
                height
            )

            normalized.append({

                "name": room["name"],

                "type": room_type,

                # ---------------------------------------------------------
                # TARGETS
                # ---------------------------------------------------------

                "target_area":
                round(final_area, 1),

                "target_width":
                round(width, 1),

                "target_height":
                round(height, 1),

                # ---------------------------------------------------------
                # BACKWARD COMPATIBILITY
                # ---------------------------------------------------------

                "area":
                round(final_area, 1),

                "width":
                round(width, 1),

                "height":
                round(height, 1),

                # ---------------------------------------------------------
                # SEMANTIC
                # ---------------------------------------------------------

                "priority":
                rules["priority"],

                "clearance":
                rules.get(
                    "clearance",
                    2.0
                ),

                "aspect":
                rules["aspect"]
            })
            
        # =========================================================
        # STORE SEMANTIC ROOM PLAN
        # =========================================================

        self.state.room_plan = normalized

        return normalized
    
    
    # =========================================================================
    # DYNAMIC DIMENSION SCALING
    # =========================================================================

    def _dynamic_dimension_scaling(

        self,

        room_type,

        width,

        height
    ):

        build_w = (
            self.state.buildable_width
        )

        build_h = (
            self.state.buildable_height
        )

        aspect = (
            self.state.buildable_aspect_ratio
        )

        # =========================================================
        # LARGE PLOTS
        # =========================================================

        if build_w > 45:

            width *= 1.08

        if build_h > 65:

            height *= 1.08

        # =========================================================
        # NARROW PLOTS
        # =========================================================

        if aspect < 0.80:

            height *= 1.10

        # =========================================================
        # WIDE PLOTS
        # =========================================================

        elif aspect > 1.25:

            width *= 1.08

        return (

            round(width, 1),

            round(height, 1)
        )
    
    # =========================================================================
    # DYNAMIC DIMENSION BIAS
    # =========================================================================

    def _dynamic_room_bias(

        self,

        room_type,

        rules
    ):

        build_w = (
            self.state.buildable_width
        )

        build_h = (
            self.state.buildable_height
        )

        aspect = (
            self.state.buildable_aspect_ratio
        )

        # =========================================================
        # WIDE PLOTS
        # =========================================================

        if aspect > 1.25:

            if room_type in {

                "living",
                "dining"
            }:

                rules["ideal"] *= 1.10

        # =========================================================
        # DEEP PLOTS
        # =========================================================

        elif aspect < 0.80:

            if room_type in {

                "bedroom",
                "master_bedroom"
            }:

                rules["ideal"] *= 1.08

        return rules

    # =========================================================================
    # USABLE AREA
    # =========================================================================

    def _compute_usable_area(self):

        if (

            hasattr(
                self.state,
                "buildable_polygon"
            )

            and

            self.state.buildable_polygon is not None
        ):

            usable_area = (

                self.state
                .buildable_polygon
                .area
            )

        else:

            usable_area = (

                self.state.plot_width
                *
                self.state.plot_height
                *
                0.55
            )

        # ---------------------------------------------------------------------
        # REMOVE OUTDOOR
        # ---------------------------------------------------------------------

        outdoor_types = {

            "parking",
            "front_lawn",
            "green_strip",
            "backyard",
            "walkway_setback"
        }

        outdoor_area = 0.0

        for s in getattr(
            self.state,
            "spaces",
            []
        ):

            if s.room_type in outdoor_types:

                outdoor_area += s.area

        usable_area -= outdoor_area

        usable_area = max(
            usable_area,
            250.0
        )

        return usable_area

    # =========================================================================
    # DERIVE DIMENSIONS
    # =========================================================================

    def _derive_dimensions(

        self,

        room_type,

        area,

        rules
    ):

        # ------------------------------------------------------------------
        # FIXED SIZE
        # ---------------------------------------------------------------------

        if (

            "fixed_width" in rules

            and

            "fixed_height" in rules
        ):

            return (

                rules["fixed_width"],
                rules["fixed_height"]
            )

        if "fixed_size" in rules:

            return rules["fixed_size"]
        
        
        # ---------------------------------------------------------------------
        # SEMANTIC PREFERRED DIMENSIONS
        # ---------------------------------------------------------------------

        preferred_w = rules.get(
            "preferred_width"
        )

        preferred_h = rules.get(
            "preferred_height"
        )

        if preferred_w and preferred_h:

            width = random.uniform(
                *preferred_w
            )

            height = area / width

            height = max(

                preferred_h[0],

                min(
                    height,
                    preferred_h[1]
                )
            )

            width, height = (

                self._dynamic_dimension_scaling(

                    room_type,

                    width,

                    height
                )
            )

            return (

                round(width, 1),

                round(height, 1)
            )

        # ---------------------------------------------------------------------
        # PREFERRED RANGE
        # ---------------------------------------------------------------------
        pw0, pw1 = rules[
            "preferred_width"
        ]

        # -------------------------------------------------------------
        # SUPPORT preferred_height
        # -------------------------------------------------------------

        if "preferred_height" in rules:

            pd0, pd1 = rules[
                "preferred_height"
            ]

        else:

            pd0, pd1 = rules[
                "preferred_depth"
            ]
            
        width = random.uniform(
            pw0,
            pw1
        )

        height = random.uniform(
            pd0,
            pd1
        )

        # ---------------------------------------------------------------------
        # TARGET AREA BALANCE
        # ---------------------------------------------------------------------

        generated_area = (
            width * height
        )

        if generated_area > 0:

            scale = sqrt(
                area / generated_area
            )

            width *= scale
            height *= scale

        # ---------------------------------------------------------------------
        # ASPECT SAFETY
        # ---------------------------------------------------------------------

        min_ratio, max_ratio = (
            rules["aspect"]
        )

        ratio = (
            width
            /
            max(height, 0.1)
        )

        if ratio < min_ratio:

            width = height * min_ratio

        elif ratio > max_ratio:

            height = width / max_ratio

        # ---------------------------------------------------------------------
        # VARIATION
        # ---------------------------------------------------------------------

        width += random.uniform(
            -0.5,
            0.5
        )

        height += random.uniform(
            -0.5,
            0.5
        )

        # ---------------------------------------------------------------------
        # CLAMP
        # ---------------------------------------------------------------------

        width = max(

            MIN_DIMENSION,

            min(
                width,
                MAX_DIMENSION
            )
        )

        height = max(

            MIN_DIMENSION,

            min(
                height,
                MAX_DIMENSION
            )
        )

        return (

            round(width, 1),

            round(height, 1)
        )

    # =========================================================================
    # LLM DIMENSION REFINEMENT
    # =========================================================================

    def _llm_refine_dimensions(

        self,

        room_type,

        width,

        height,

        area
    ):

        # ---------------------------------------------------------------------
        # KEEP SIMPLE FOR SPEED
        # ---------------------------------------------------------------------

        try:

            prompt = f"""
You are an expert architectural dimensional planner.

Refine room dimensions ergonomically.

ROOM TYPE:
{room_type}

CURRENT:
width={width}
height={height}
area={area}

Rules:
- preserve architectural realism
- preserve ergonomic circulation
- avoid narrow rooms
- avoid unrealistic aspect ratios
- kitchen ergonomic
- utility compact
- dining circulation-friendly

Return STRICT JSON:

{{
  "width": 10,
  "height": 8
}}
"""

            response = self.client.chat.completions.create(

                model="gpt-4.1-mini",

                temperature=0.05,

                messages=[

                    {
                        "role": "system",

                        "content":
                        "Return valid JSON only."
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

            content = re.sub(
                r"```json",
                "",
                content
            )

            content = re.sub(
                r"```",
                "",
                content
            )

            data = json.loads(
                content
            )

            width = float(
                data.get(
                    "width",
                    width
                )
            )

            height = float(
                data.get(
                    "height",
                    height
                )
            )

        except Exception:
            pass

        return (

            round(width, 1),

            round(height, 1)
        )