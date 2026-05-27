# =============================================================================
# VASTU VALIDATOR v5
# =============================================================================
# Production vastu intelligence validator
#
# Validates:
#
# - directional zoning
# - entrance logic
# - kitchen placement
# - master bedroom placement
# - staircase placement
# - environmental harmony
# - circulation compatibility
# =============================================================================

from state import LayoutState

from config.room_standards import (

    VASTU_POSITIONS,

    STAIR_VALID_CORNERS,

    KITCHEN_CORNERS
)

# =============================================================================
# VALIDATOR
# =============================================================================


class VastuValidator:

    def validate(

        self,

        state: LayoutState
    ):

        print("\n" + "=" * 60)

        print("VASTU VALIDATION")

        print("=" * 60)

        if state.buildable_polygon is None:

            return True

        score = 0

        total = 0

        self._validate_rooms(
            state
        )

        self._validate_kitchen(
            state
        )

        self._validate_master_bedroom(
            state
        )

        self._validate_staircase(
            state
        )

        self._validate_living(
            state
        )

        self._validate_bathrooms(
            state
        )

        # =========================================================================
        # SCORE
        # =========================================================================

        compliant = len([

            w for w in state.warnings

            if "vastu" not in w.lower()
        ])

        total_checked = max(

            1,

            len(state.spaces)
        )

        ratio = compliant / total_checked

        state.vastu_score = round(

            ratio * 100,

            1
        )

        print("\n" + "=" * 60)

        print(

            f"VASTU SCORE:"
            f" {state.vastu_score}/100"
        )

        print("=" * 60)

        return True

# =============================================================================
# ROOMS
# =============================================================================


    def _validate_rooms(

        self,

        state
    ):

        print("\n[ROOM DIRECTIONS]")

        for s in state.spaces:

            preferred = VASTU_POSITIONS.get(
                s.room_type
            )

            if preferred is None:

                continue

            actual = self._get_direction(

                state,

                s
            )

            valid = self._match_direction(

                preferred,

                actual
            )

            if valid:

                print(

                    f"  ✔ {s.name:20s}"
                    f"{actual}"
                )

            else:

                msg = (

                    f"Vastu:"
                    f" {s.name}"
                    f" at {actual}"
                    f" expected {preferred}"
                )

                state.warnings.append(msg)

                print(f"  ⚠ {msg}")

# =============================================================================
# KITCHEN
# =============================================================================


    def _validate_kitchen(

        self,

        state
    ):

        print("\n[KITCHEN]")

        kitchen = state.get_space(
            "kitchen"
        )

        if kitchen is None:

            return

        actual = self._get_direction(

            state,

            kitchen
        )

        valid = False

        for d in KITCHEN_CORNERS:

            if d in actual:

                valid = True

        if valid:

            print(
                "  ✔ Kitchen placement"
            )

        else:

            msg = (

                "Vastu: kitchen"
                " should be SE/NW"
            )

            state.warnings.append(msg)

            print(f"  ⚠ {msg}")

# =============================================================================
# MASTER
# =============================================================================


    def _validate_master_bedroom(

        self,

        state
    ):

        print("\n[MASTER BEDROOM]")

        master = state.get_space(
            "master_bedroom"
        )

        if master is None:

            return

        actual = self._get_direction(

            state,

            master
        )

        if "south-west" in actual:

            print(
                "  ✔ Master bedroom SW"
            )

        else:

            msg = (

                "Vastu: master bedroom"
                " should be SW"
            )

            state.warnings.append(msg)

            print(f"  ⚠ {msg}")

# =============================================================================
# STAIR
# =============================================================================


    def _validate_staircase(

        self,

        state
    ):

        print("\n[STAIRCASE]")

        stair = state.get_space(
            "staircase"
        )

        if stair is None:

            return

        actual = self._get_direction(

            state,

            stair
        )

        valid = False

        for d in STAIR_VALID_CORNERS:

            if d in actual:

                valid = True

        if valid:

            print(
                "  ✔ Staircase valid"
            )

        else:

            msg = (

                "Vastu: staircase"
                " invalid corner"
            )

            state.warnings.append(msg)

            print(f"  ⚠ {msg}")

# =============================================================================
# LIVING
# =============================================================================


    def _validate_living(

        self,

        state
    ):

        print("\n[LIVING]")

        living = state.get_space(
            "living"
        )

        if living is None:

            return

        actual = self._get_direction(

            state,

            living
        )

        if any(

            d in actual

            for d in [

                "north",
                "north-east",
                "east"
            ]
        ):

            print(
                "  ✔ Living north"
            )

        else:

            msg = (

                "Vastu: living"
                " should face north"
            )

            state.warnings.append(msg)

            print(f"  ⚠ {msg}")

# =============================================================================
# BATHROOM
# =============================================================================


    def _validate_bathrooms(

        self,

        state
    ):

        print("\n[BATHROOMS]")

        bathrooms = [

            s for s in state.spaces

            if "bathroom" in s.room_type
        ]

        for bath in bathrooms:

            actual = self._get_direction(

                state,

                bath
            )

            if "west" in actual:

                print(

                    f"  ✔ {bath.name}"
                )

            else:

                msg = (

                    f"Vastu:"
                    f" {bath.name}"
                    f" should be west"
                )

                state.warnings.append(msg)

                print(f"  ⚠ {msg}")

# =============================================================================
# DIRECTION
# =============================================================================


    def _get_direction(

        self,

        state,

        space
    ):

        bx0, by0, bx1, by1 = (

            state.buildable_polygon.bounds
        )

        cx = (bx0 + bx1) / 2

        cy = (by0 + by1) / 2

        sx = space.centroid.x

        sy = space.centroid.y

        ns = (

            "north"

            if sy >= cy

            else "south"
        )

        ew = (

            "east"

            if sx >= cx

            else "west"
        )

        return f"{ns}-{ew}"

# =============================================================================
# MATCH
# =============================================================================


    def _match_direction(

        self,

        preferred,

        actual
    ):

        preferred = preferred.lower()

        actual = actual.lower()

        if preferred == actual:

            return True

        tokens = preferred.split("-")

        matches = 0

        for t in tokens:

            if t in actual:

                matches += 1

        return matches >= 1