# =============================================================================
# GHMC + TOPOLOGY-AWARE SETBACK ENGINE v2
# =============================================================================
# Production architectural setback logic
# for ArchiVerse topology engine
#
# FEATURES
# - GHMC adaptive setbacks
# - one-side plant strip only
# - compact backyard logic
# - utility-side intelligence
# - topology-aware front reduction
# - adaptive side setbacks
# =============================================================================

from typing import Dict

from config.constants import (
    SQFT_TO_SQM,
    METER_TO_FEET,
    PLANT_STRIP,
    FRONT_OPEN_MIN_DEPTH
)

# =============================================================================
# GHMC
# =============================================================================

class GHMC:

    # =========================================================================
    # RAW GHMC TIERS (meters)
    # =========================================================================

    TIERS = [

        # (max_area_sqm, front, rear, side)

        (100, 1.5, 0.5, 0.5),

        (200, 1.5, 1.0, 1.0),

        (300, 2.0, 1.0, 1.0),

        (500, 3.0, 1.5, 1.5),

        (1000, 4.0, 2.0, 2.0),
    ]

    DEFAULT_TIER = (
        5.0,
        3.0,
        3.0
    )

    # =========================================================================
    # INTERNAL
    # =========================================================================

    @classmethod
    def _raw_setbacks_m(
        cls,
        plot_area_sqm: float
    ):

        for max_area, front, rear, side in cls.TIERS:

            if plot_area_sqm <= max_area:

                return (
                    front,
                    rear,
                    side
                )

        return cls.DEFAULT_TIER

    # =========================================================================
    # ADAPTIVE SIDE SETBACK
    # =========================================================================

    @classmethod
    def _adaptive_side_ft(
        cls,
        plot_area_sqm,
        base_side_ft
    ):

        if plot_area_sqm < 120:

            return max(3.0, base_side_ft)

        elif plot_area_sqm < 250:

            return max(4.0, base_side_ft)

        elif plot_area_sqm < 500:

            return max(5.0, base_side_ft)

        return max(6.0, base_side_ft)

    # =========================================================================
    # MAIN ENGINE
    # =========================================================================

    @classmethod
    def setbacks(
        cls,
        plot_area_sqm: float,
        facing: str,
        has_parking: bool = True,
        has_lawn: bool = True,
        has_backyard: bool = False,
        has_plants: bool = False,
        plant_side: str = "left",
    ) -> Dict[str, float]:

        """
        Returns directional setbacks in FEET.
        """

        front_m, rear_m, side_m = cls._raw_setbacks_m(
            plot_area_sqm
        )

        # =====================================================
        # CONVERT TO FEET
        # =====================================================

        front_ft = round(
            front_m * METER_TO_FEET,
            2
        )

        rear_ft = round(
            rear_m * METER_TO_FEET,
            2
        )

        side_ft = round(
            side_m * METER_TO_FEET,
            2
        )

        # =====================================================
        # ADAPTIVE SIDE LOGIC
        # =====================================================

        side_ft = cls._adaptive_side_ft(
            plot_area_sqm,
            side_ft
        )

        # =====================================================
        # FRONT OPENNESS REDUCTION
        # =====================================================

        if has_parking and has_lawn:

            front_ft *= 0.70

        elif has_parking or has_lawn:

            front_ft *= 0.85

        front_ft = max(
            front_ft,
            5.0
        )

        # =====================================================
        # BACKYARD LOGIC
        # =====================================================

        # backyard is localized court
        # NOT full-width strip

        if has_backyard:

            rear_ft *= 0.60

            rear_ft = max(
                rear_ft,
                2.0
            )

        # =====================================================
        # DIRECTIONAL MAPPING
        # =====================================================

        facing = facing.lower()

        OPPOSITE = {

            "north": "south",

            "south": "north",

            "east": "west",

            "west": "east",
        }

        setbacks = {}

        for direction in (
            "north",
            "south",
            "east",
            "west"
        ):

            # =================================================
            # FRONT
            # =================================================

            if direction == facing:

                setbacks[direction] = round(
                    front_ft,
                    2
                )

            # =================================================
            # REAR
            # =================================================

            elif direction == OPPOSITE[facing]:

                setbacks[direction] = round(
                    rear_ft,
                    2
                )

            # =================================================
            # SIDES
            # =================================================

            else:

                setbacks[direction] = round(
                    side_ft,
                    2
                )

        # =====================================================
        # ONE-SIDE PLANT STRIP ONLY
        # =====================================================

        if has_plants:

            if facing in ["north", "south"]:

                if plant_side == "left":

                    setbacks["west"] += PLANT_STRIP

                else:

                    setbacks["east"] += PLANT_STRIP

            else:

                if plant_side == "left":

                    setbacks["south"] += PLANT_STRIP

                else:

                    setbacks["north"] += PLANT_STRIP

        # =====================================================
        # UTILITY SIDE
        # =====================================================

        utility_side = "rear"

        # compact plots shift utility sideways

        if plot_area_sqm < 180:

            if facing in ["north", "south"]:

                utility_side = "east"

            else:

                utility_side = "south"

        setbacks["utility_side"] = utility_side

        return setbacks

    # =========================================================================
    # BUILDABLE BOUNDARY
    # =========================================================================

    @classmethod
    def buildable_dimensions(
        cls,
        plot_width: float,
        plot_height: float,
        setbacks: Dict[str, float]
    ) -> Dict[str, float]:

        buildable_width = (

            plot_width

            - setbacks["east"]

            - setbacks["west"]
        )

        buildable_height = (

            plot_height

            - setbacks["north"]

            - setbacks["south"]
        )

        return {

            "width": round(
                max(buildable_width, 0),
                2
            ),

            "height": round(
                max(buildable_height, 0),
                2
            ),

            "area": round(
                max(buildable_width, 0)
                *
                max(buildable_height, 0),
                2
            )
        }

    # =========================================================================
    # DEBUG
    # =========================================================================

    @classmethod
    def debug(
        cls,
        setbacks: Dict[str, float]
    ):

        print("\n  [GHMC SETBACKS]")

        for side, value in setbacks.items():

            if side == "utility_side":

                print(
                    f"    {'UTILITY':10s}"
                    f": {value}"
                )

            else:

                print(
                    f"    {side.upper():10s}"
                    f": {value:.2f} ft"
                )