# =============================================================================
# REFINEMENT ENGINE v5
# =============================================================================
# Production architectural refinement engine
#
# Handles:
#
# - aspect ratio correction
# - topology cleanup
# - overlap cleanup
# - corridor refinement
# - room alignment
# - wall alignment
# - dead-space absorption
# - compactness optimization
# - environmental balancing
# =============================================================================
import os
import sys

UTILS_DIR = os.path.abspath(

    os.path.join(

        os.path.dirname(__file__),

        "../utils"
    )
)

if UTILS_DIR not in sys.path:

    sys.path.insert(
        0,
        UTILS_DIR
    )
    
    
from shapely.geometry import (
    Polygon,
    MultiPolygon
)

from shapely.ops import (
    unary_union
)

from state import (
    LayoutState,
    Space
)

from config.constants import *

from geometry_utils import (

    aspect_ratio,

    compactness,

    polygon_quality_score,

    shared_wall_length,

    are_adjacent
)

# =============================================================================
# ENGINE
# =============================================================================


class RefinementEngine:

    def refine(

        self,

        state: LayoutState
    ):

        print("\n" + "=" * 60)

        print("REFINEMENT ENGINE")

        print("=" * 60)

        self._fix_aspect_ratios(
            state
        )

        self._align_walls(
            state
        )

        self._improve_compactness(
            state
        )

        self._merge_micro_spaces(
            state
        )

        self._cleanup_corridors(
            state
        )

        self._refine_environmental_spaces(
            state
        )

        self._score_quality(
            state
        )

        print("\n✔ Refinement complete")

# =============================================================================
# ASPECT
# =============================================================================


    def _fix_aspect_ratios(

        self,

        state
    ):

        print("\n[ASPECT REFINEMENT]")

        for s in state.spaces:

            ratio = aspect_ratio(
                s.polygon
            )

            if ratio <= 5:

                continue

            minx, miny, maxx, maxy = (

                s.polygon.bounds
            )

            w = maxx - minx

            h = maxy - miny

            # =============================================================
            # stretch short side
            # =============================================================

            if w > h:

                target_h = max(

                    h,

                    w / 3
                )

                center = (miny + maxy) / 2

                new_min = center - (target_h / 2)

                new_max = center + (target_h / 2)

                s.polygon = Polygon([

                    (minx, new_min),
                    (maxx, new_min),

                    (maxx, new_max),
                    (minx, new_max)
                ])

            else:

                target_w = max(

                    w,

                    h / 3
                )

                center = (minx + maxx) / 2

                new_min = center - (target_w / 2)

                new_max = center + (target_w / 2)

                s.polygon = Polygon([

                    (new_min, miny),
                    (new_max, miny),

                    (new_max, maxy),
                    (new_min, maxy)
                ])

            print(

                f"  ✔ {s.name}"
                f" ratio refined"
            )

# =============================================================================
# ALIGN
# =============================================================================


    def _align_walls(

        self,

        state
    ):

        print("\n[WALL ALIGNMENT]")

        for i in range(len(state.spaces)):

            for j in range(i + 1, len(state.spaces)):

                a = state.spaces[i]
                b = state.spaces[j]

                shared = shared_wall_length(

                    a.polygon,
                    b.polygon
                )

                if shared < 2:

                    continue

                ax0, ay0, ax1, ay1 = (

                    a.polygon.bounds
                )

                bx0, by0, bx1, by1 = (

                    b.polygon.bounds
                )

                # =============================================================
                # snap close walls
                # =============================================================

                tolerance = 0.5

                if abs(ax1 - bx0) < tolerance:

                    bx0 = ax1

                if abs(bx1 - ax0) < tolerance:

                    ax0 = bx1

                if abs(ay1 - by0) < tolerance:

                    by0 = ay1

                if abs(by1 - ay0) < tolerance:

                    ay0 = by1

                a.polygon = Polygon([

                    (ax0, ay0),
                    (ax1, ay0),

                    (ax1, ay1),
                    (ax0, ay1)
                ])

                b.polygon = Polygon([

                    (bx0, by0),
                    (bx1, by0),

                    (bx1, by1),
                    (bx0, by1)
                ])

        print(
            "  ✔ Walls aligned"
        )

# =============================================================================
# COMPACTNESS
# =============================================================================


    def _improve_compactness(

        self,

        state
    ):

        print("\n[COMPACTNESS]")

        for s in state.spaces:

            comp = compactness(
                s.polygon
            )

            if comp >= 0.15:

                continue

            buffered = s.polygon.buffer(
                0.5
            )

            if buffered.area > s.area * 1.4:

                continue

            s.polygon = buffered

            print(

                f"  ✔ {s.name}"
                f" compactness improved"
            )

# =============================================================================
# MICRO SPACES
# =============================================================================


    def _merge_micro_spaces(

        self,

        state
    ):

        print("\n[MICRO SPACES]")

        remove = []

        for s in state.spaces:

            if s.area > 20:

                continue

            nearest = None

            nearest_dist = 999

            for other in state.spaces:

                if other == s:

                    continue

                d = s.polygon.distance(
                    other.polygon
                )

                if d < nearest_dist:

                    nearest_dist = d

                    nearest = other

            if nearest:

                nearest.polygon = unary_union([

                    nearest.polygon,
                    s.polygon
                ])

                remove.append(s)

                print(

                    f"  ✔ merged {s.name}"
                    f" → {nearest.name}"
                )

        for r in remove:

            if r in state.spaces:

                state.spaces.remove(r)

# =============================================================================
# CORRIDORS
# =============================================================================


    def _cleanup_corridors(

        self,

        state
    ):

        print("\n[CORRIDORS]")

        remove = []

        for s in state.spaces:

            if s.room_type != "corridor":

                continue

            ratio = aspect_ratio(
                s.polygon
            )

            if ratio > 20:

                remove.append(s)

                continue

            if s.area < 10:

                remove.append(s)

        for r in remove:

            state.spaces.remove(r)

        print(

            f"  ✔ Removed:"
            f" {len(remove)}"
        )

# =============================================================================
# ENVIRONMENT
# =============================================================================


    def _refine_environmental_spaces(

        self,

        state
    ):

        print("\n[ENVIRONMENTAL]")

        env_spaces = [

            s for s in state.spaces

            if s.zone == "environmental"
        ]

        for s in env_spaces:

            if s.area < 15:

                s.polygon = s.polygon.buffer(
                    1
                )

        print(
            "  ✔ Environmental refinement"
        )

# =============================================================================
# QUALITY
# =============================================================================


    def _score_quality(

        self,

        state
    ):

        print("\n[QUALITY SCORE]")

        total = 0

        count = 0

        for s in state.spaces:

            q = polygon_quality_score(
                s.polygon
            )

            total += q

            count += 1

            print(

                f"  {s.name:20s}"
                f"{q:.1f}/100"
            )

        if count == 0:

            return

        avg = total / count

        print(

            f"\n  Average:"
            f" {avg:.1f}/100"
        )