# =============================================================================
# ZONING ENGINE v12
# =============================================================================
# FIXED SEMANTIC ARCHITECTURAL ZONING
#
# FIXES:
# - semantic priorities were becoming 0.000
# - privacy hierarchy was empty
# - confidence logic broken
# - living wrongly becoming private
# - topology relationships exploding
# - better architectural defaults
# =============================================================================

from typing import Dict

from state import LayoutState

# =============================================================================
# ENGINE
# =============================================================================

class ZoningEngine:

    # =========================================================================
    # MAIN
    # =========================================================================

    def apply_zones(

        self,

        state: LayoutState
    ):

        print("\n" + "=" * 60)

        print("SEMANTIC ZONING ENGINE")

        print("=" * 60)

        # =============================================================
        # AI OUTPUT
        # =============================================================

        if state.gnn_zones:

            print("\n[SEMANTIC AI OUTPUT]")

            for room, info in state.gnn_zones.items():

                print(

                    f"  {room:20s}"

                    f"{info.get('zone','?'):15s}"

                    f"SEM={info.get('semantic_priority',0):.3f}"
                )

        # =============================================================
        # SYNTHESIS
        # =============================================================

        final_zones = self._synthesize_zones(
            state
        )

        state.final_zones = final_zones

        # =============================================================
        # RELATIONSHIPS
        # =============================================================

        relationships = self._build_relationships(
            final_zones
        )

        state.topology_relationships = (
            relationships
        )

        # =============================================================
        # PRIVACY
        # =============================================================

        privacy = self._privacy_gradient(
            final_zones
        )

        state.privacy_hierarchy = privacy

        # =============================================================
        # ENVIRONMENT
        # =============================================================

        environmental = self._environmental_groups(
            final_zones
        )

        state.environmental_groups = (
            environmental
        )

        # =============================================================
        # WET ZONES
        # =============================================================

        plumbing = self._wet_zone_groups(
            final_zones
        )

        state.wet_zone_groups = plumbing

        # =============================================================
        # LOG
        # =============================================================

        self._log_results(
            state
        )

    # =========================================================================
    # SYNTHESIS
    # =========================================================================

    def _synthesize_zones(

        self,

        state
    ):

        final = {}

        room_plan = getattr(

            state,

            "room_plan",

            []
        )

        for room in room_plan:

            name = room["name"]

            room_type = room["type"]

            gnn = state.gnn_zones.get(
                name,
                {}
            )

            # =========================================================
            # FIXED DIRECT VALUES
            # =========================================================

            zone = gnn.get(
                "zone",
                self._default_zone(room_type)
            )

            privacy = gnn.get(
                "privacy",
                self._default_privacy(room_type)
            )

            circulation = gnn.get(
                "circulation",
                self._default_circulation(room_type)
            )

            frontage = gnn.get(
                "frontage",
                self._default_frontage(room_type)
            )

            # =========================================================
            # FIXED PRIORITY
            # =========================================================

            semantic_priority = gnn.get(

                "semantic_priority",

                self._default_priority(room_type)
            )

            # =========================================================
            # SAFETY
            # =========================================================

            semantic_priority = max(

                0.1,

                float(semantic_priority)
            )

            # =========================================================
            # LIVING SAFETY
            # =========================================================

            if room_type == "living":

                zone = "social"
                privacy = "public"
                circulation = "high"
                frontage = "high"

                semantic_priority = max(
                    semantic_priority,
                    0.95
                )

            # =========================================================
            # DINING SAFETY
            # =========================================================

            if room_type == "dining":

                zone = "social"

                semantic_priority = max(
                    semantic_priority,
                    0.88
                )

            # =========================================================
            # KITCHEN SAFETY
            # =========================================================

            if room_type == "kitchen":

                zone = "service"

                semantic_priority = max(
                    semantic_priority,
                    0.90
                )

            # =========================================================
            # BEDROOM SAFETY
            # =========================================================

            if "bedroom" in room_type:

                zone = "private"
                privacy = "private"

                semantic_priority = max(
                    semantic_priority,
                    0.82
                )

            # =========================================================
            # BATHROOM SAFETY
            # =========================================================

            if "bathroom" in room_type:

                zone = "service"

                semantic_priority = max(
                    semantic_priority,
                    0.70
                )

            final[name] = {

                "zone": zone,

                "privacy": privacy,

                "circulation": circulation,

                "frontage": frontage,

                "semantic_priority": round(
                    semantic_priority,
                    3
                )
            }

        return final

    # =========================================================================
    # RELATIONSHIPS
    # =========================================================================

    def _build_relationships(

        self,

        zones
    ):

        relationships = []

        names = list(
            zones.keys()
        )

        for i in range(len(names)):

            for j in range(i + 1, len(names)):

                a = names[i]
                b = names[j]

                score = self._relationship_weight(
                    a,
                    b
                )

                if score <= 0:
                    continue

                relationships.append({

                    "a": a,
                    "b": b,
                    "weight": score
                })

        relationships.sort(

            key=lambda x: x["weight"],

            reverse=True
        )

        return relationships

    # =========================================================================
    # RELATIONSHIP WEIGHT
    # =========================================================================

    def _relationship_weight(

        self,

        a,

        b
    ):

        score = 0

        # =============================================================
        # LIVING ↔ DINING
        # =============================================================

        if (

            ("living" in a and "dining" in b)

            or

            ("living" in b and "dining" in a)
        ):

            score += 30

        # =============================================================
        # KITCHEN ↔ DINING
        # =============================================================

        if (

            ("kitchen" in a and "dining" in b)

            or

            ("kitchen" in b and "dining" in a)
        ):

            score += 28

        # =============================================================
        # KITCHEN ↔ WASH
        # =============================================================

        if (

            ("kitchen" in a and "wash" in b)

            or

            ("kitchen" in b and "wash" in a)
        ):

            score += 35

        # =============================================================
        # KITCHEN ↔ STORE
        # =============================================================

        if (

            ("kitchen" in a and "store" in b)

            or

            ("kitchen" in b and "store" in a)
        ):

            score += 32

        # =============================================================
        # BEDROOM ↔ BATHROOM
        # =============================================================

        if (

            ("bedroom" in a and "bathroom" in b)

            or

            ("bedroom" in b and "bathroom" in a)
        ):

            score += 24

        # =============================================================
        # BEDROOM ↔ LIVING
        # =============================================================

        if (

            ("bedroom" in a and "living" in b)

            or

            ("bedroom" in b and "living" in a)
        ):

            score += 8

        # =============================================================
        # STAIR ↔ LIVING
        # =============================================================

        if (

            ("stair" in a and "living" in b)

            or

            ("stair" in b and "living" in a)
        ):

            score += 16

        return score

    # =========================================================================
    # PRIVACY
    # =========================================================================

    def _privacy_gradient(

        self,

        zones
    ):

        result = {

            "public": [],
            "semi_private": [],
            "private": []
        }

        for room, info in zones.items():

            p = info["privacy"]

            if p not in result:

                p = "semi_private"

            result[p].append(room)

        return result

    # =========================================================================
    # ENVIRONMENT
    # =========================================================================

    def _environmental_groups(

        self,

        zones
    ):

        result = []

        for room, info in zones.items():

            frontage = info.get(
                "frontage",
                "low"
            )

            if frontage in [

                "medium",
                "high"
            ]:

                result.append(room)

        return result

    # =========================================================================
    # WET GROUPS
    # =========================================================================

    def _wet_zone_groups(

        self,

        zones
    ):

        result = []

        for room in zones:

            if any(

                x in room

                for x in [

                    "bathroom",
                    "kitchen",
                    "wash"
                ]
            ):

                result.append(room)

        return result

    # =========================================================================
    # DEFAULTS
    # =========================================================================

    def _default_zone(

        self,

        room_type
    ):

        mapping = {

            "living": "social",
            "dining": "social",

            "kitchen": "service",
            "wash_area": "service",
            "store": "service",

            "master_bedroom": "private",
            "bedroom": "private",

            "bathroom": "service",

            "parking": "semi_private",
            "staircase": "semi_private"
        }

        return mapping.get(
            room_type,
            "semi_private"
        )

    def _default_privacy(

        self,

        room_type
    ):

        if room_type in [

            "living",
            "dining"

        ]:

            return "public"

        if room_type in [

            "kitchen",
            "wash_area",
            "store"
        ]:

            return "semi_private"

        if (

            "bedroom" in room_type
            or
            "bathroom" in room_type
        ):

            return "private"

        return "semi_private"

    def _default_circulation(

        self,

        room_type
    ):

        if room_type == "living":

            return "high"

        if room_type in [

            "dining",
            "staircase"
        ]:

            return "medium"

        return "low"

    def _default_frontage(

        self,

        room_type
    ):

        if room_type in [

            "living",
            "dining"
        ]:

            return "high"

        if "bedroom" in room_type:

            return "medium"

        return "low"

    def _default_priority(

        self,

        room_type
    ):

        priorities = {

            "living": 0.98,

            "kitchen": 0.95,
            "dining": 0.90,

            "master_bedroom": 0.88,
            "bedroom": 0.84,

            "bathroom": 0.72,

            "wash_area": 0.80,
            "store": 0.78
        }

        return priorities.get(
            room_type,
            0.5
        )

    # =========================================================================
    # LOGGING
    # =========================================================================

    def _log_results(

        self,

        state
    ):

        print("\n[FINAL SEMANTIC ZONES]")

        for room, info in state.final_zones.items():

            print(

                f"  {room:20s}"

                f"{info['zone']:15s}"

                f"PRIV={info['privacy']:12s}"

                f"SEM={info['semantic_priority']:.3f}"
            )

        print("\n[TOP RELATIONSHIPS]")

        for r in state.topology_relationships[:15]:

            print(

                f"  {r['a']:20s}"

                f"{r['b']:20s}"

                f"{r['weight']}"
            )

        print("\n[PRIVACY HIERARCHY]")

        for k, v in state.privacy_hierarchy.items():

            print(

                f"  {k:15s}"

                f"{len(v)} rooms"
            )

        print("\n✔ Semantic zoning complete")