# =============================================================================
# LAYOUT STATE v20
# =============================================================================

from __future__ import annotations

from dataclasses import dataclass, field

from typing import (
    List,
    Dict,
    Optional,
    Any
)

from shapely.geometry import (
    Polygon,
    MultiPolygon
)

# =============================================================================
# SPACE
# =============================================================================

@dataclass
class Space:

    name: str

    room_type: str

    polygon: Polygon

    zone: str = "indoor"

    attached_to: str = ""

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    # =========================================================================
    # GEOMETRY SAFETY
    # =========================================================================

    @property
    def is_valid(self):

        if self.polygon is None:
            return False

        return (

            not self.polygon.is_empty
            and
            self.polygon.is_valid
        )

    @property
    def is_empty(self):

        if self.polygon is None:
            return True

        return self.polygon.is_empty

    @property
    def bounds(self):

        if not self.is_valid:
            return (0, 0, 0, 0)

        return self.polygon.bounds

    @property
    def centroid(self):

        if not self.is_valid:
            return None

        return self.polygon.centroid

    @property
    def exterior(self):

        if not self.is_valid:
            return None

        return self.polygon.exterior

    # =========================================================================
    # DIMENSIONS
    # =========================================================================

    @property
    def area(self):

        if not self.is_valid:
            return 0.0

        return round(
            self.polygon.area,
            2
        )

    @property
    def width(self):

        if not self.is_valid:
            return 0.0

        minx, _, maxx, _ = self.bounds

        return round(
            maxx - minx,
            2
        )

    @property
    def height(self):

        if not self.is_valid:
            return 0.0

        _, miny, _, maxy = self.bounds

        return round(
            maxy - miny,
            2
        )

    # =========================================================================
    # DEBUG
    # =========================================================================

    def __repr__(self):

        return (

            f"Space("
            f"{self.name}, "
            f"{self.room_type}, "
            f"{self.area:.1f} sqft)"
        )

# =============================================================================
# LAYOUT STATE
# =============================================================================

@dataclass
class LayoutState:

    # =========================================================================
    # INPUT
    # =========================================================================

    plot_width: float = 40

    plot_height: float = 60

    facing: str = "north"

    bedrooms: int = 2

    bathrooms: int = 2

    road_width: float = 30

    optional_rooms: List[str] = field(
        default_factory=list
    )

    requirements: Dict[str, Any] = field(
        default_factory=dict
    )

    # =========================================================================
    # GEOMETRY
    # =========================================================================

    plot_polygon: Optional[Polygon] = None

    buildable_polygon: Optional[Polygon] = None

    remaining_polygon: Optional[Polygon] = None

    residual_polygon: Optional[Polygon] = None

    # =========================================================================
    # SPACES
    # =========================================================================

    spaces: List[Space] = field(
        default_factory=list
    )

    walls: List[Any] = field(
        default_factory=list
    )

    # =========================================================================
    # PIPELINE DATA
    # =========================================================================

    room_plan: List[Dict[str, Any]] = field(
        default_factory=list
    )

    llm_plan: Dict[str, Any] = field(
        default_factory=dict
    )

    topology: Dict[str, Any] = field(
        default_factory=dict
    )

    rules: Dict[str, Any] = field(
        default_factory=dict
    )

    validation: Dict[str, Any] = field(
        default_factory=dict
    )

    topology_score: Dict[str, Any] = field(
        default_factory=dict
    )

    adjacency_graph: Dict[str, Any] = field(
        default_factory=dict
    )

    semantic_layout: Dict[str, Any] = field(
        default_factory=dict
    )
    
    # =========================================================================
    # SEMANTIC TOPOLOGY
    # =========================================================================

    semantic_topology: Dict[str, Any] = field(
        default_factory=dict
    )

    topology_targets: Dict[str, Any] = field(
        default_factory=dict
    )

    dynamic_zones: Dict[str, Any] = field(
        default_factory=dict
    )

    corner_occupancy: Dict[str, Any] = field(
        default_factory=dict
    )

    aspect_ratio_data: Dict[str, Any] = field(
        default_factory=dict
    )
    
    service_logic: Dict[str, Any] = field(
        default_factory=dict
    )

    # =========================================================================
    # SEMANTIC SERVICE CLUSTERING
    # =========================================================================

    service_cluster: Dict[str, Any] = field(
        default_factory=dict
    )
    
    # =========================================================================
    # SEMANTIC CONTROL FLAGS
    # =========================================================================

    keep_living_simple: bool = True

    kitchen_scale_bias: float = 1.35

    # =========================================================================
    # GNN OUTPUTS
    # =========================================================================

    gnn_predictions: Dict[str, Any] = field(
        default_factory=dict
    )

    adjacency_predictions: Dict[str, Any] = field(
        default_factory=dict
    )

    circulation_predictions: Dict[str, Any] = field(
        default_factory=dict
    )

    frontage_predictions: Dict[str, Any] = field(
        default_factory=dict
    )

    privacy_predictions: Dict[str, Any] = field(
        default_factory=dict
    )

    # =========================================================================
    # DEBUG
    # =========================================================================

    errors: List[str] = field(
        default_factory=list
    )

    warnings: List[str] = field(
        default_factory=list
    )

    debug_log: List[str] = field(
        default_factory=list
    )

    layout_score: float = 0.0

    score: float = 0.0

    # =========================================================================
    # UTILIZATION
    # =========================================================================

    @property
    def utilisation(self):

        if (

            self.buildable_polygon is None

            or

            self.buildable_polygon.is_empty
        ):
            return 0.0

        ignore = {

            "green_strip",
            "walkway_setback",
            "backyard",
            "front_lawn",
            "parking",
            "main_gate",
            "staircase"
        }

        used = 0.0

        for s in self.spaces:

            if s.room_type in ignore:
                continue

            used += s.area

        return min(

            used
            /
            max(
                self.buildable_polygon.area,
                1.0
            ),

            1.0
        )

    # =========================================================================
    # ROAD SIDE
    # =========================================================================

    @property
    def road_side(self):

        return self.facing

    # =========================================================================
    # HELPERS
    # =========================================================================

    def get_space(self, name):

        for s in self.spaces:

            if s.name == name:
                return s

        for s in self.spaces:

            if s.room_type == name:
                return s

        return None

    def get_spaces_by_type(self, room_type):

        return [

            s for s in self.spaces

            if s.room_type == room_type
        ]

    def remove_space(self, name):

        self.spaces = [

            s for s in self.spaces

            if s.name != name
        ]

    def has_space(self, room_type):

        return any(

            s.room_type == room_type

            for s in self.spaces
        )
        
    # =========================================================================
    # BUILDABLE ANALYTICS
    # =========================================================================

    @property
    def buildable_width(self):

        if self.buildable_polygon is None:
            return 0.0

        bx0, _, bx1, _ = (
            self.buildable_polygon.bounds
        )

        return bx1 - bx0


    @property
    def buildable_height(self):

        if self.buildable_polygon is None:
            return 0.0

        _, by0, _, by1 = (
            self.buildable_polygon.bounds
        )

        return by1 - by0


    @property
    def buildable_aspect_ratio(self):

        return (

            self.buildable_width

            /

            max(self.buildable_height, 1)
        )

    # =========================================================================
    # DEBUG
    # =========================================================================

    def log(self, msg):

        self.debug_log.append(msg)

        print(f"[STATE] {msg}")

    def debug(self):

        print("\n" + "=" * 60)
        print("LAYOUT STATE")
        print("=" * 60)

        print(
            f"Spaces       : "
            f"{len(self.spaces)}"
        )

        print(
            f"Utilisation  : "
            f"{self.utilisation*100:.1f}%"
        )

        print(
            f"Errors       : "
            f"{len(self.errors)}"
        )

        print(
            f"Warnings     : "
            f"{len(self.warnings)}"
        )