# =============================================================================
# ARCHIVERSE — SEMANTIC TOPOLOGY PREPROCESSOR v6
# =============================================================================
# COMPLETE VERSION
#
# FEATURES:
# - semantic graph generation
# - edge_attr support
# - doorway graph
# - visibility graph
# - privacy depth
# - circulation intelligence
# - graph topology metrics
# - multi-task targets
# - adjacency compatibility targets
# - graph-level embeddings targets
# - luxury score
# - openness score
# - vastu score
# - style labels
# - architectural reasoning features
# =============================================================================

import os
import json
import pickle
import math

import networkx as nx
import numpy as np

from tqdm import tqdm

from shapely.geometry import (
    Polygon,
    MultiPolygon,
    LineString
)

# =============================================================================
# PATHS
# =============================================================================

RAW_PATH = (
    r"C:\Users\jyoth\Desktop\Major-Project\Backend"
    r"\datasets\raw\Layout\ResPlan\ResPlan.pkl"
)

SAVE_PATH = (
    r"C:\Users\jyoth\Desktop\Major-Project\Backend"
    r"\datasets\processed\Layout\resplan_semantic_graph_v6.json"
)

# =============================================================================
# LABELS
# =============================================================================

ROOM_LABELS = {

    "living": 0,
    "kitchen": 1,
    "bedroom": 2,
    "bathroom": 3,
    "balcony": 4,
    "storage": 5,
    "stair": 6,
    "parking": 7,
    "garden": 8
}

ZONE_MAPPING = {

    "living": 0,
    "balcony": 0,

    "bedroom": 1,
    "bathroom": 1,

    "kitchen": 2,
    "storage": 2,
    "stair": 2,

    "parking": 3,
    "garden": 3
}

STYLE_LABELS = {

    "compact": 0,
    "modern": 1,
    "luxury": 2
}

# =============================================================================
# HELPERS
# =============================================================================

def polygon_list(geom):

    if geom is None:
        return []

    if isinstance(geom, Polygon):
        return [geom]

    if isinstance(geom, MultiPolygon):
        return list(geom.geoms)

    return []


def normalize(v, mx):

    if mx == 0:
        return 0.0

    return float(v / mx)


def compactness(poly):

    if poly.area == 0:
        return 0.0

    return (
        4 * math.pi * poly.area
    ) / (poly.length ** 2)


def touches_boundary(poly, land):

    try:

        return poly.boundary.intersects(
            land.boundary
        )

    except:
        return False


def shared_wall_length(poly1, poly2):

    try:

        inter = poly1.boundary.intersection(
            poly2.boundary
        )

        return float(inter.length)

    except:
        return 0.0


def centroid_distance(poly1, poly2):

    return poly1.centroid.distance(
        poly2.centroid
    )


def line_visibility(poly1, poly2, walls):

    try:

        c1 = poly1.centroid
        c2 = poly2.centroid

        line = LineString([
            (c1.x, c1.y),
            (c2.x, c2.y)
        ])

        if walls is None:
            return 1

        return int(
            not line.intersects(walls)
        )

    except:
        return 0


def door_connected(poly1, poly2, doors):

    try:

        if doors is None:
            return 0

        for d in polygon_list(doors):

            if (
                d.distance(poly1) < 2
                and
                d.distance(poly2) < 2
            ):
                return 1

        return 0

    except:
        return 0

# =============================================================================
# LABEL HELPERS
# =============================================================================

def privacy_label(room_type):

    if room_type in [
        "bedroom",
        "bathroom"
    ]:
        return 2

    if room_type in [
        "kitchen",
        "storage"
    ]:
        return 1

    return 0


def circulation_label(room_type):

    if room_type in [
        "living",
        "stair"
    ]:
        return 2

    if room_type == "kitchen":
        return 1

    return 0


def frontage_label(room_type):

    if room_type in [
        "living",
        "balcony",
        "garden"
    ]:
        return 2

    if room_type == "bedroom":
        return 1

    return 0

# =============================================================================
# ADJACENCY COMPATIBILITY
# =============================================================================

COMPATIBILITY = {

    ("living", "kitchen"): 0.9,
    ("kitchen", "living"): 0.9,

    ("living", "bedroom"): 0.6,
    ("bedroom", "living"): 0.6,

    ("bedroom", "bathroom"): 0.95,
    ("bathroom", "bedroom"): 0.95,

    ("kitchen", "bathroom"): 0.8,
    ("bathroom", "kitchen"): 0.8,

    ("living", "balcony"): 0.95,
    ("balcony", "living"): 0.95,

    ("bathroom", "living"): 0.2,
    ("living", "bathroom"): 0.2
}

def adjacency_score(a, b):

    return COMPATIBILITY.get(
        (a, b),
        0.5
    )

# =============================================================================
# GRAPH TARGETS
# =============================================================================

def openness_score(room_instances):

    open_rooms = 0

    for r in room_instances:

        if r["room_type"] in [
            "living",
            "balcony",
            "garden"
        ]:
            open_rooms += 1

    return min(
        open_rooms / max(len(room_instances), 1),
        1.0
    )


def luxury_score(room_instances):

    total_area = 0

    for r in room_instances:

        total_area += r["polygon"].area

    avg_area = total_area / max(
        len(room_instances),
        1
    )

    return min(avg_area / 5000, 1.0)


def vastu_score(room_instances):

    score = 0

    for r in room_instances:

        room_type = r["room_type"]

        poly = r["polygon"]

        cx = poly.centroid.x
        cy = poly.centroid.y

        if room_type == "kitchen":

            if cx > 0 and cy < 0:
                score += 1

        if room_type == "living":

            score += 0.5

    return min(score / 5.0, 1.0)


def style_label(openness, luxury):

    if luxury > 0.65:
        return STYLE_LABELS["luxury"]

    if openness > 0.35:
        return STYLE_LABELS["modern"]

    return STYLE_LABELS["compact"]

# =============================================================================
# LOAD RAW
# =============================================================================

print("\nLOADING RAW DATASET...\n")

with open(RAW_PATH, "rb") as f:

    raw = pickle.load(f)

print(f"TOTAL SAMPLES: {len(raw)}")

# =============================================================================
# PROCESS
# =============================================================================

processed = []

for sample_idx, sample in enumerate(tqdm(raw)):

    try:

        land = sample["land"]

        walls = sample.get("wall")
        doors = sample.get("door")
        windows = sample.get("window")
        garden = sample.get("garden")

        front_door = sample.get(
            "front_door"
        )

        unit_type = sample.get(
            "unitType",
            "unknown"
        )

        lx0, ly0, lx1, ly1 = land.bounds

        land_w = lx1 - lx0
        land_h = ly1 - ly0

        # =====================================================================
        # ROOM INSTANCES
        # =====================================================================

        room_instances = []

        for room_type in ROOM_LABELS.keys():

            geom = sample.get(room_type)

            if geom is None:
                continue

            polys = polygon_list(geom)

            for poly_idx, poly in enumerate(polys):

                room_instances.append({

                    "room_name":
                    f"{room_type}_{poly_idx}",

                    "room_type":
                    room_type,

                    "polygon":
                    poly
                })

        # =====================================================================
        # GRAPH
        # =====================================================================

        G = nx.Graph()

        x = []

        room_labels = []
        zone_labels = []

        privacy_labels = []
        circulation_labels = []
        frontage_labels = []

        # =====================================================================
        # NODE FEATURES
        # =====================================================================

        for idx, room in enumerate(room_instances):

            poly = room["polygon"]
            room_type = room["room_type"]

            cx = poly.centroid.x
            cy = poly.centroid.y

            minx, miny, maxx, maxy = poly.bounds

            w = maxx - minx
            h = maxy - miny

            x_norm = normalize(
                cx - lx0,
                land_w
            )

            y_norm = normalize(
                cy - ly0,
                land_h
            )

            exterior_touch = int(
                touches_boundary(poly, land)
            )

            corner_room = int(

                exterior_touch and (

                    x_norm < 0.2
                    or
                    x_norm > 0.8
                )
            )

            distance_from_entrance = 0.0

            if front_door is not None:

                distance_from_entrance = normalize(

                    poly.distance(front_door),

                    max(land_w, land_h)
                )

            ventilation_score = float(
                exterior_touch
            )

            sunlight_score = float(
                y_norm
            )

            frontage_score = float(
                1.0 - distance_from_entrance
            )

            wet_wall_score = float(

                room_type in [
                    "kitchen",
                    "bathroom"
                ]
            )

            north_score = y_norm
            south_score = 1 - y_norm

            east_score = x_norm
            west_score = 1 - x_norm

            north_east = (
                north_score * east_score
            )

            north_west = (
                north_score * west_score
            )

            south_east = (
                south_score * east_score
            )

            south_west = (
                south_score * west_score
            )

            near_window = 0

            if windows is not None:

                near_window = int(
                    poly.distance(windows) < 3
                )

            near_garden = 0

            if garden is not None:

                near_garden = int(
                    poly.distance(garden) < 5
                )

            features = [

                # geometry
                x_norm,
                y_norm,

                normalize(w, land_w),
                normalize(h, land_h),

                normalize(
                    poly.area,
                    land.area
                ),

                w / max(h, 0.01),

                compactness(poly),

                # topology
                exterior_touch,
                corner_room,

                # architectural
                distance_from_entrance,
                ventilation_score,
                sunlight_score,
                frontage_score,
                wet_wall_score,

                # orientation
                north_score,
                south_score,
                east_score,
                west_score,

                north_east,
                north_west,
                south_east,
                south_west,

                # environment
                near_window,
                near_garden
            ]

            x.append(features)

            room_labels.append(
                ROOM_LABELS[room_type]
            )

            zone_labels.append(
                ZONE_MAPPING[room_type]
            )

            privacy_labels.append(
                privacy_label(room_type)
            )

            circulation_labels.append(
                circulation_label(room_type)
            )

            frontage_labels.append(
                frontage_label(room_type)
            )

            G.add_node(idx)

        # =====================================================================
        # EDGES
        # =====================================================================

        edge_index = []
        edge_attr = []

        adjacency_targets = []

        for i in range(len(room_instances)):

            for j in range(i + 1, len(room_instances)):

                room_a = room_instances[i]
                room_b = room_instances[j]

                poly_a = room_a["polygon"]
                poly_b = room_b["polygon"]

                type_a = room_a["room_type"]
                type_b = room_b["room_type"]

                dist = centroid_distance(
                    poly_a,
                    poly_b
                )

                if dist < max(land_w, land_h) * 0.35:

                    shared_len = shared_wall_length(
                        poly_a,
                        poly_b
                    )

                    visibility = line_visibility(
                        poly_a,
                        poly_b,
                        walls
                    )

                    door_conn = door_connected(
                        poly_a,
                        poly_b,
                        doors
                    )

                    plumbing_conn = float(

                        type_a in [
                            "kitchen",
                            "bathroom"
                        ]
                        and
                        type_b in [
                            "kitchen",
                            "bathroom"
                        ]
                    )

                    circulation_conn = float(

                        type_a in [
                            "living",
                            "stair"
                        ]
                        or
                        type_b in [
                            "living",
                            "stair"
                        ]
                    )

                    hierarchy_conn = float(

                        type_a == "living"
                        or
                        type_b == "living"
                    )

                    compatibility = adjacency_score(
                        type_a,
                        type_b
                    )

                    edge_features = [

                        normalize(
                            shared_len,
                            max(land_w, land_h)
                        ),

                        normalize(
                            dist,
                            max(land_w, land_h)
                        ),

                        visibility,
                        door_conn,

                        plumbing_conn,
                        circulation_conn,
                        hierarchy_conn
                    ]

                    edge_index.append([i, j])
                    edge_index.append([j, i])

                    edge_attr.append(edge_features)
                    edge_attr.append(edge_features)

                    adjacency_targets.append(
                        compatibility
                    )

                    adjacency_targets.append(
                        compatibility
                    )

                    G.add_edge(i, j)

        # =====================================================================
        # GRAPH METRICS
        # =====================================================================

        degree_cent = nx.degree_centrality(G)

        try:

            between_cent = nx.betweenness_centrality(
                G
            )

        except:

            between_cent = {}

        # =====================================================================
        # ENTRANCE NODE
        # =====================================================================

        entrance_node = 0

        min_dist = 999999

        if front_door is not None:

            for idx, room in enumerate(room_instances):

                d = room["polygon"].distance(
                    front_door
                )

                if d < min_dist:

                    min_dist = d
                    entrance_node = idx

        # =====================================================================
        # FINAL NODE FEATURES
        # =====================================================================

        for idx in range(len(x)):

            privacy_depth = 0.0
            circulation_distance = 0.0

            try:

                path_len = nx.shortest_path_length(
                    G,
                    entrance_node,
                    idx
                )

                privacy_depth = normalize(
                    path_len,
                    len(room_instances)
                )

                circulation_distance = normalize(
                    path_len,
                    len(room_instances)
                )

            except:
                pass

            x[idx].extend([

                degree_cent.get(idx, 0.0),

                between_cent.get(idx, 0.0),

                privacy_depth,

                circulation_distance
            ])

        # =====================================================================
        # GRAPH TARGETS
        # =====================================================================

        open_score = openness_score(
            room_instances
        )

        lux_score = luxury_score(
            room_instances
        )

        vastu = vastu_score(
            room_instances
        )

        style = style_label(
            open_score,
            lux_score
        )

        # =====================================================================
        # GRAPH ATTR
        # =====================================================================

        graph_attr = {

            "sample_id": sample_idx,

            "plot_area": land.area,

            "plot_width": land_w,

            "plot_height": land_h,

            "plot_aspect_ratio": (
                land_w / max(land_h, 0.01)
            ),

            "unit_type": unit_type
        }

        # =====================================================================
        # SAVE
        # =====================================================================

        processed.append({

            "x": x,

            "edge_index": edge_index,

            "edge_attr": edge_attr,

            "room_labels": room_labels,

            "zone_labels": zone_labels,

            "privacy_labels": privacy_labels,

            "circulation_labels": circulation_labels,

            "frontage_labels": frontage_labels,

            "adjacency_targets":
            adjacency_targets,

            "graph_targets": {

                "openness_score":
                open_score,

                "luxury_score":
                lux_score,

                "vastu_score":
                vastu,

                "style_label":
                style
            },

            "graph_attr": graph_attr
        })

    except Exception as e:

        print(f"\nERROR SAMPLE {sample_idx}")
        print(e)

# =============================================================================
# SAVE
# =============================================================================

os.makedirs(
    os.path.dirname(SAVE_PATH),
    exist_ok=True
)

with open(SAVE_PATH, "w") as f:

    json.dump(processed, f)

print("\n" + "=" * 70)
print("SEMANTIC TOPOLOGY DATASET v6 CREATED")
print("=" * 70)

print(f"\nTOTAL GRAPHS: {len(processed)}")

print(f"\nSAVED TO:\n{SAVE_PATH}")