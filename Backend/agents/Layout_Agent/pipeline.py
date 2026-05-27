# =============================================================================
# pipeline.py
# =============================================================================
# ARCHIVERSE PIPELINE v34
# =============================================================================

from copy import deepcopy
import json

from state import LayoutState

from geometry.boundary_manager import (
    create_plot_boundary,
    generate_buildable_core
)

from ai.layout_reasoner import (
    LayoutReasoner
)

from ai.intelligent_space_programmer import (
    IntelligentSpaceProgrammer
)

from ai.adjacency_planner import (
    build_adjacency_graph
)

from ai.service_cluster_reasoner import (
    ServiceClusterReasoner
)

from planning.topology_solver import (
    TopologySolver
)

from rendering.layout_renderer import (
    render_all_variants
)

# =============================================================================
# ROOM REQUIREMENTS
# =============================================================================

def generate_room_requirements(
    bhk
):

    rooms = [

        {
            "name": "living",
            "type": "living"
        },

        {
            "name": "dining",
            "type": "dining"
        },

        {
            "name": "kitchen",
            "type": "kitchen"
        },

        {
            "name": "store",
            "type": "store"
        },

        {
            "name": "utility",
            "type": "utility"
        },

        {
            "name": "wash_area",
            "type": "wash_area"
        },

        {
            "name": "master_bedroom",
            "type": "master_bedroom"
        }
    ]

    # ============================================================
    # SECONDARY BEDROOMS
    # ============================================================

    for i in range(max(0, bhk - 1)):

        rooms.append({

            "name": f"bedroom_{i+1}",

            "type": "bedroom"
        })

    # ============================================================
    # BATHROOMS
    # ============================================================

    rooms.append({

        "name": "master_toilet",

        "type": "bathroom"
    })

    for i in range(max(0, bhk - 1)):

        rooms.append({

            "name": f"bedroom_toilet_{i+1}",

            "type": "bathroom"
        })

    return rooms

# =============================================================================
# MAIN PIPELINE
# =============================================================================

def run_pipeline(

    input_data,

    variants=1,

    render=True
):

    print("\n" + "=" * 80)
    print("ARCHIVERSE PIPELINE v34")
    print("=" * 80)

    generated = []

    # =========================================================================
    # INPUTS
    # =========================================================================

    facing = input_data.get(
        "facing"
    ).lower()

    # =========================================================================
    # PLOT
    # =========================================================================

    if "plot" in input_data:

        plot_width, plot_height = (
            input_data["plot"]
        )

    else:

        plot_width = input_data.get(
            "plot_width"
        )

        plot_height = input_data.get(
            "plot_height"
        )

    # =========================================================================
    # BHK
    # =========================================================================

    bhk = (

        input_data.get("bhk")

        or

        input_data.get("bedrooms")

        or

        2
    )

    # =========================================================================
    # PLOT POLYGON
    # =========================================================================

    plot_polygon = create_plot_boundary(

        plot_width,

        plot_height
    )

    # =========================================================================
    # SINGLE STABLE VARIANT
    # =========================================================================

    try:

        state = LayoutState()
        
        # ============================================================
        # PLOT DIMENSIONS
        # REQUIRED FOR RENDERER
        # ============================================================

        state.plot_width = plot_width
        state.plot_height = plot_height

        state.variant_id = 1
        state.variant_mode = "stable"

        state.facing = facing

        state.plot_polygon = plot_polygon

        # =========================================================================
        # BUILDABLE
        # =========================================================================

        state.buildable_polygon = (

            generate_buildable_core(

                plot_polygon=plot_polygon,

                frontage_polygons=[],

                environmental_polygons=[],

                facing=facing
            )
        )

        if state.buildable_polygon is None:

            print(
                "✘ invalid buildable polygon"
            )

            return []

        # =========================================================================
        # ROOM REQUIREMENTS
        # =========================================================================

        room_requirements = generate_room_requirements(
            bhk
        )

        # =========================================================================
        # LLM TOPOLOGY
        # =========================================================================

        reasoner = LayoutReasoner()

        llm_plan = reasoner.generate_layout_logic({

            "plot": {

                "width": plot_width,

                "height": plot_height
            },

            "facing": facing,

            "bedrooms": bhk,

            "bathrooms": bhk,

            "optional_rooms": []
        })

        state.llm_plan = llm_plan

        state.topology = llm_plan.get(
            "topology",
            {}
        )

        state.rules = llm_plan.get(
            "placement_rules",
            {}
        )

        print("\n[LLM TOPOLOGY]")

        print(
            json.dumps(
                llm_plan,
                indent=2
            )
        )

        # =========================================================================
        # SPACE PROGRAMMER
        # =========================================================================

        programmer = IntelligentSpaceProgrammer(
            state
        )

        room_plan = programmer.generate_program(
            room_requirements
        )

        state.room_plan = room_plan

        # =========================================================================
        # ADJACENCY GRAPH
        # =========================================================================

        room_names = [

            r["name"]

            for r in room_plan
        ]

        adjacency_graph = (

            build_adjacency_graph(

                gnn_zones=state.topology,

                llm_plan=llm_plan,

                room_names=room_names
            )
        )

        state.topology["adjacency_graph"] = (
            adjacency_graph
        )

        # =========================================================================
        # ROOM PROGRAM DEBUG
        # =========================================================================

        print("\n[ROOM PROGRAM]")

        for r in room_plan:

            print(

                f"  {r['name']:18s}"

                f"{r['target_area']:7.1f} sqft"

                f"   "

                f"{r['target_width']:.1f}"

                f" x "

                f"{r['target_height']:.1f}"
            )

        # =========================================================================
        # SERVICE CLUSTER REASONING
        # =========================================================================

        service_reasoner = (

            ServiceClusterReasoner(

                facing=facing,

                buildable_polygon=state.buildable_polygon,

                residual_polygon=None,

                adjacency_graph=adjacency_graph
            )
        )

        service_logic = (

            service_reasoner.reason_service_cluster(

                kitchen_node={

                    "type": "kitchen"
                }
            )
        )

        state.service_cluster = (
            service_logic
        )

        # =========================================================================
        # SEMANTIC TOPOLOGY
        # =========================================================================

        state.semantic_variant = {

            "north": ["NE"],

            "east": ["NW"],

            "south": ["SW"],

            "west": ["NE"]
        }

        # =========================================================================
        # TOPOLOGY SOLVER
        # =========================================================================

        solver = TopologySolver()

        success = solver.solve_topology(

            state,

            room_plan
        )
        
        # =========================================================
        # ATTACHED BATHROOM GENERATION
        # =========================================================

        from planning.plumbing_engine import PlumbingEngine

        plumbing = PlumbingEngine(
            engine=solver,
            state=state
        )

        bedrooms = [

            s for s in state.spaces

            if s.room_type in [
                "master_bedroom",
                "bedroom"
            ]
        ]

        for bedroom in bedrooms:

            # avoid duplicates
            already = False

            for s in state.spaces:

                if s.room_type == "bathroom":

                    if s.polygon.intersects(
                        bedroom.polygon
                    ):
                        already = True
                        break

            if already:
                continue

            # =====================================================
            # CREATE INTERNAL BATH
            # =====================================================

            _, bath = plumbing.place_internal_bathroom(

                bedroom.polygon,

                {
                    "width": 5,
                    "height": 7
                }
            )

            if bath is None:
                continue

            # =====================================================
            # CREATE SIMPLE BATHROOM OBJECT
            # =====================================================

            class BathroomSpace:
                pass

            bathroom_space = BathroomSpace()

            bathroom_space.name = (
                f"{bedroom.name}_bath"
            )

            bathroom_space.room_type = (
                "bathroom"
            )

            bathroom_space.polygon = bath

            bathroom_space.zone = "service"

            bathroom_space.centroid = (
                bath.centroid
            )

            state.spaces.append(
                bathroom_space
            )

        if not success:

            print(
                "✘ topology failed"
            )

            return []

        generated = [
            deepcopy(state)
        ]

        print(
            "\n✔ final layout complete"
        )

    except Exception as e:

        print(f"\n[PIPELINE ERROR] {e}")

        import traceback

        traceback.print_exc()

        return []

    # =========================================================================
    # RENDER
    # =========================================================================

    if render and generated:

        render_all_variants(

            generated,

            {

                "plot": [

                    plot_width,

                    plot_height
                ],

                "facing": facing
            }
        )

    print("\n" + "=" * 80)
    print("PIPELINE COMPLETE")
    print("=" * 80)

    print(
        f"Generated Variants : "
        f"{len(generated)}"
    )

    return [generated[0]]