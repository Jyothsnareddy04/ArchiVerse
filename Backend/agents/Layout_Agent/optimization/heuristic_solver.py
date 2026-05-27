# =============================================================================
# optimization/heuristic_solver.py
# =============================================================================

from math import sqrt

# =============================================================================
# ROOM PROGRAM
# =============================================================================

ROOM_PROGRAM = {

    "living": {
        "target_area": 280,
        "min_area": 180,
        "max_area": 420,
        "aspect_ratio": (1.0, 2.0)
    },

    "master_bedroom": {
        "target_area": 200,
        "min_area": 150,
        "max_area": 260,
        "aspect_ratio": (1.0, 1.8)
    },

    "bedroom": {
        "target_area": 150,
        "min_area": 110,
        "max_area": 220,
        "aspect_ratio": (1.0, 1.7)
    },

    "kitchen": {
        "target_area": 120,
        "min_area": 90,
        "max_area": 180,
        "aspect_ratio": (1.0, 1.5)
    },

    "bathroom": {
        "target_area": 34,
        "min_area": 24,
        "max_area": 50,
        "aspect_ratio": (1.0, 1.8)
    },

    "dining": {
        "target_area": 140,
        "min_area": 100,
        "max_area": 220,
        "aspect_ratio": (1.0, 1.8)
    },

    "store": {
        "target_area": 25,
        "min_area": 16,
        "max_area": 40,
        "aspect_ratio": (1.0, 2.0)
    },

    "wash_area": {
        "target_area": 40,
        "min_area": 30,
        "max_area": 60,
        "aspect_ratio": (1.0, 2.0)
    }
}

# =============================================================================
# ENGINE
# =============================================================================

class HeuristicSolver:

    def optimize_program(

        self,

        state,

        room_plan
    ):

        print("\n[HEURISTIC PROGRAMMING]")

        optimized = []

        plot_area = (

            state.plot_width
            *
            state.plot_height
        )

        scale_factor = min(

            max(
                plot_area / 2400.0,
                0.82
            ),

            1.18
        )

        for room in room_plan:

            room_type = room["type"]

            if room_type not in ROOM_PROGRAM:

                optimized.append(room)

                continue

            rules = ROOM_PROGRAM[
                room_type
            ]

            target = (
                rules["target_area"]
                *
                scale_factor
            )

            min_ar, max_ar = (
                rules["aspect_ratio"]
            )

            aspect = (
                min_ar + max_ar
            ) / 2

            width = sqrt(
                target * aspect
            )

            height = (
                target / width
            )

            width = round(width, 1)
            height = round(height, 1)

            room["target_area"] = round(
                target,
                1
            )

            room["width"] = width
            room["height"] = height

            room["min_area"] = rules[
                "min_area"
            ]

            room["max_area"] = rules[
                "max_area"
            ]

            print(

                f"  ✔ {room['name']:20s}"
                f"{width:.1f}x{height:.1f}"
                f" = {target:.1f} sqft"
            )

            optimized.append(room)

        return optimized