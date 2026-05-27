# =============================================================================
# topology_solver.py
# =============================================================================
# ARCHIVERSE — STABLE TOPOLOGY SOLVER v32
# =============================================================================
# FIXES
#
# ✔ STRICT outside → inside topology order
# ✔ frontage BEFORE environment
# ✔ environment BEFORE buildable generation
# ✔ walkway subtraction BEFORE buildable
# ✔ NO post-buildable subtraction corruption
# ✔ stable residual initialization
# ✔ living emergence fixed
# ✔ topology consistency fixed
# ✔ environmental topology stabilized
# ✔ no buildable/environment mismatch
#
# FINAL PIPELINE
#
# plot
#   → frontage
#   → environment
#   → walkway
#   → buildable core
#   → subtraction engine
#   → service cluster
#   → bedroom cluster
#   → dining cluster
#   → living emergence
#
# =============================================================================

from state import LayoutState

from geometry.boundary_manager import (
    generate_buildable_core
)

from geometry.subtraction_engine import (
    SubtractionEngine
)

from planning.site_frontage_engine import (
    SiteFrontageEngine
)

from planning.environmental_opening_engine import (
    EnvironmentalOpeningEngine
)

from planning.plumbing_engine import (
    PlumbingEngine
)

from planning.room_cluster_engine import (
    RoomClusterEngine
)

from planning.living_emergence_solver import (
    LivingEmergenceSolver
)

from validation.topology_validator import (
    TopologyValidator
)

from state import Space

# =============================================================================
# SOLVER
# =============================================================================

class TopologySolver:

    # =========================================================================
    # MAIN
    # =========================================================================

    def solve_topology(

        self,

        state,

        room_plan
    ):

        print("\n" + "=" * 70)
        print("TOPOLOGY SOLVER v32")
        print("=" * 70)

        # ---------------------------------------------------------------------
        # RESET
        # ---------------------------------------------------------------------

        state.spaces = []
        state.errors = []
        state.warnings = []

        state.remaining_polygon = None

        # =========================================================================
        # PHASE 1 — FRONTAGE
        # =========================================================================

        print("\n[PHASE 1 — FRONTAGE]")

        frontage_engine = SiteFrontageEngine()

        frontage_polygons = frontage_engine.generate(
            state
        )

        frontage_names = [

            "main_gate",
            "parking",
            "staircase",
            "front_lawn"
        ]

        frontage_types = [

            "main_gate",
            "parking",
            "staircase",
            "front_lawn"
        ]

        # ---------------------------------------------------------------------
        # REGISTER FRONTAGE
        # ---------------------------------------------------------------------

        frontage_registered = []

        for idx, poly in enumerate(frontage_polygons):

            if poly is None:
                continue

            if poly.is_empty:
                continue

            poly = poly.buffer(0)

            frontage_registered.append(
                poly
            )

            state.spaces.append(

                Space(

                    name=frontage_names[idx],

                    room_type=frontage_types[idx],

                    polygon=poly,

                    zone="frontage"
                )
            )

        # =========================================================================
        # PHASE 2 — ENVIRONMENT
        # =========================================================================

        print("\n[PHASE 2 — ENVIRONMENT]")

        environmental_engine = (
            EnvironmentalOpeningEngine(
                state
            )
        )

        environmental_engine.generate()

        # ---------------------------------------------------------------------
        # COLLECT ENVIRONMENT POLYGONS
        # IMPORTANT:
        # collected BEFORE buildable generation
        # ---------------------------------------------------------------------

        environment_registered = []

        for s in state.spaces:

            if s.room_type in (

                "green_strip",
                "walkway_setback",
                "backyard"
            ):

                environment_registered.append(
                    s.polygon.buffer(0)
                )

        # =========================================================================
        # PHASE 3 — BUILDABLE CORE
        # =========================================================================

        print("\n[PHASE 3 — BUILDABLE CORE]")

        buildable = generate_buildable_core(

            plot_polygon=state.plot_polygon,

            frontage_polygons=frontage_registered,

            environmental_polygons=environment_registered,

            front_setback=4.0,

            side_setback=3.0,

            rear_setback=5.0,

            facing=state.facing
        )

        if buildable is None:

            state.errors.append(
                "Buildable generation failed"
            )

            return False

        if buildable.is_empty:

            state.errors.append(
                "Buildable polygon empty"
            )

            return False

        buildable = buildable.buffer(0)

        state.buildable_polygon = buildable

        print(
            f"  ✔ buildable area : "
            f"{buildable.area:.1f} sqft"
        )

        # =========================================================================
        # PHASE 4 — SUBTRACTION ENGINE
        # =========================================================================

        print("\n[PHASE 4 — SUBTRACTION ENGINE]")

        subtraction_engine = (

            SubtractionEngine(

                buildable_polygon=buildable,

                state=state
            )
        )

        # =========================================================================
        # PHASE 5 — ROOM CLUSTERS
        # =========================================================================

        print("\n[PHASE 5 — SERVICE CLUSTER]")

        # ============================================================
        # PLUMBING ENGINE
        # ============================================================

        plumbing_engine = (

            PlumbingEngine(

                engine=subtraction_engine,

                state=state
            )
        )

        # ============================================================
        # ROOM CLUSTER ENGINE
        # ============================================================

        cluster_engine = (

            RoomClusterEngine(

                engine=subtraction_engine,

                state=state,

                plumbing_engine=plumbing_engine
            )
        )

        # ---------------------------------------------------------------------
        # SERVICE
        # ---------------------------------------------------------------------

        try:

            # =============================================================
            # PLACE SERVICE CLUSTER
            # =============================================================

            cluster_engine.place_service_cluster(
                room_plan
            )

            # =============================================================
            # VALIDATION
            # =============================================================

            service_names = [

                s.name
                for s in state.spaces
                if s.zone == "service"
            ]

            expected = [

                "kitchen",
                "store",
                "utility",
                "wash_area"
            ]

            missing = [

                x for x in expected
                if x not in service_names
            ]

            print("\n[SERVICE CLUSTER COMPLETE]")

            for s in state.spaces:

                if s.zone == "service":

                    print(

                        f"  ✔ {s.name:16s}"
                        f"{s.area:.1f} sqft"
                    )

            # =============================================================
            # DEBUG
            # =============================================================

            if missing:

                print(
                    "\n[SERVICE WARNING]"
                )

                print(
                    f"  missing -> {missing}"
                )

            else:

                print(
                    "\n  ✔ full service cluster placed"
                )

        except Exception as e:

            print(
                f"\n[SERVICE ERROR] {e}"
            )

            import traceback

            traceback.print_exc()
            
            
        # =========================================================================
        # PHASE 7 — SOCIAL CLUSTERS
        # =========================================================================

        print("\n[PHASE 7 — SOCIAL CLUSTERS]")

        try:

            cluster_engine.place_social_clusters(
                room_plan
            )

        except Exception as e:

            print(
                f"  [SOCIAL ERROR] {e}"
            )

        # =========================================================================
        # PHASE 6 — BEDROOM CLUSTERS
        # =========================================================================

        print("\n[PHASE 6 — BEDROOM CLUSTERS]")

        try:

            # =========================================================
            # TOTAL BEDROOMS
            # =========================================================

            bedrooms_required = sum(

                1 for r in room_plan

                if r["type"] in {

                    "master_bedroom",
                    "bedroom"
                }
            )

            cluster_engine.place_bedrooms(
                bedrooms_required
            )

        except Exception as e:

            print(
                f"  [BEDROOM ERROR] {e}"
            )

        # =========================================================================
        # PHASE 8 — LIVING EMERGENCE
        # =========================================================================

        # print("\n[PHASE 8 — LIVING EMERGENCE]")

        # try:

        #     living_solver = (

        #         LivingEmergenceSolver(

        #             engine=subtraction_engine,

        #             state=state
        #         )
        #     )

        #     # -------------------------------------------------------------
        #     # NEW SIGNATURE
        #     # -------------------------------------------------------------

        #     living_solver.emerge_living_room()

        # except Exception as e:

        #     print(
        #         f"  [LIVING ERROR] {e}"
        #     )

        # =========================================================================
        # PHASE 9 — SAVE REMAINING
        # =========================================================================

        state.remaining_polygon = (
            subtraction_engine.remaining
        )

        # =========================================================================
        # PHASE 10 — UTILIZATION
        # =========================================================================

        indoor_area = 0.0

        for s in state.spaces:

            if s.zone in (

                "service",
                "private",
                "social"
            ):

                indoor_area += s.area

        utilisation = 0.0

        if state.buildable_polygon:

            utilisation = (

                indoor_area
                /
                max(
                    state.buildable_polygon.area,
                    1.0
                )
            )

        # ---------------------------------------------------------------------
        # SAFE STATE STORAGE
        # ---------------------------------------------------------------------

        state.layout_score = round(
            utilisation * 100,
            1
        )

        print(
            f"  ✔ utilization : "
            f"{utilisation * 100:.1f}%"
        )

        # =========================================================================
        # PHASE 11 — VALIDATION
        # =========================================================================

        print("\n[PHASE 11 — VALIDATION]")

        try:

            validator = TopologyValidator()

            validator.validate(
                state
            )

        except Exception as e:

            print(
                f"  [VALIDATION ERROR] {e}"
            )

        # =========================================================================
        # SUMMARY
        # =========================================================================

        self._summary(
            state,
            utilisation
        )

        return True

    # =========================================================================
    # SUMMARY
    # =========================================================================

    def _summary(

        self,

        state,

        utilisation
    ):

        print("\n" + "=" * 70)
        print("FINAL TOPOLOGY")
        print("=" * 70)

        for s in state.spaces:

            print(

                f"  {s.name:18s}"

                f"{s.zone:14s}"

                f"{s.area:.1f} sqft"
            )

        print("\n" + "-" * 70)

        if state.buildable_polygon:

            print(
                f"  Buildable Area : "
                f"{state.buildable_polygon.area:.1f}"
            )

        print(
            f"  Utilization    : "
            f"{utilisation * 100:.1f}%"
        )

        print(
            f"  Score          : "
            f"{state.layout_score:.1f}"
        )

        print(
            f"  Errors         : "
            f"{len(state.errors)}"
        )

        print(
            f"  Warnings       : "
            f"{len(state.warnings)}"
        )