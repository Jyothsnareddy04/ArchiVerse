# =============================================================================
# AI / GNN ZONING v11
# =============================================================================
# FIXED VERSION
#
# FIXES:
# - correct checkpoint loading
# - correct model architecture loading
# - proper feature dimensions
# - runtime compatibility with trained model
# - safe edge handling
# - stable semantic inference
# =============================================================================

import os
import sys
import importlib.util

from typing import List
from typing import Dict

import torch
import networkx as nx
from torch_geometric.data import Data

# =============================================================================
# PATHS
# =============================================================================

import os
import sys
import torch

CURRENT_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

GRAPH_MODEL_DIR = os.path.abspath(

    os.path.join(

        CURRENT_DIR,

        "../../../models/Layout/Graph_model"
    )
)

# =============================================================================
# CHECKPOINT
# =============================================================================

MODEL_PATH = os.path.join(

    GRAPH_MODEL_DIR,

    "checkpoints",

    "semantic_topology_gnn_v2.pt"
)

# =============================================================================
# DEVICE
# =============================================================================

DEVICE = torch.device(

    "cuda"

    if torch.cuda.is_available()

    else "cpu"
)

# =============================================================================
# ADD GRAPH MODEL PATH
# =============================================================================

if GRAPH_MODEL_DIR not in sys.path:

    sys.path.insert(
        0,
        GRAPH_MODEL_DIR
    )

# =============================================================================
# IMPORT TRAINED MODEL
# =============================================================================

from model import SemanticGNN

# =============================================================================
# VERIFY
# =============================================================================

print("\nMODEL DIRECTORY\n")

print(GRAPH_MODEL_DIR)

print("\nMODEL ARCHITECTURE\n")

temp_model = SemanticGNN()

print(temp_model)

# =============================================================================
# LABELS
# =============================================================================

ZONE_LABELS = {

    0: "social",
    1: "private",
    2: "service",
    3: "exterior"
}

PRIVACY_LABELS = {

    0: "public",
    1: "semi_private",
    2: "private"
}

CIRCULATION_LABELS = {

    0: "low",
    1: "medium",
    2: "high"
}

FRONTAGE_LABELS = {

    0: "low",
    1: "medium",
    2: "high"
}

# =============================================================================
# GLOBAL MODEL
# =============================================================================

MODEL = None

# =============================================================================
# LOAD MODEL
# =============================================================================

# =============================================================================
# LOAD MODEL
# =============================================================================

def load_model():

    global MODEL

    if MODEL is not None:

        return MODEL

    print("\n[LOADING SEMANTIC GNN]")

    try:

        MODEL = SemanticGNN()

        checkpoint = torch.load(

            MODEL_PATH,

            map_location=DEVICE
        )

        # =============================================================
        # EXTRACT STATE DICT
        # =============================================================

        if isinstance(checkpoint, dict):

            if "model_state_dict" in checkpoint:

                state_dict = checkpoint[
                    "model_state_dict"
                ]

            else:

                state_dict = checkpoint

        else:

            state_dict = checkpoint

        # =============================================================
        # LOAD WEIGHTS
        # =============================================================

        MODEL.load_state_dict(
            state_dict
        )

        MODEL.to(DEVICE)

        MODEL.eval()

        print("\n✔ GNN WEIGHTS LOADED")

        return MODEL

    except Exception as e:

        print("\n⚠ GNN WEIGHT LOAD FAILED")

        print(e)

        MODEL = None

        return None

# =============================================================================
# NODE FEATURES
# =============================================================================

def build_node_features(

    rooms,

    adjacency_pairs,

    plot_width,

    plot_height
):

    G = nx.Graph()

    for room in rooms:

        G.add_node(room["name"])

    for a, b in adjacency_pairs:

        G.add_edge(a, b)

    degree_cent = nx.degree_centrality(G)

    between_cent = nx.betweenness_centrality(
        G,
        normalized=True
    )

    features = []

    total_area = max(
        plot_width * plot_height,
        1
    )

    for room in rooms:

        room_name = room["name"]

        room_type = room["type"]

        x = room.get("x", 0)
        y = room.get("y", 0)

        width = room.get("width", 10)
        height = room.get("height", 10)

        area = width * height

        nx_pos = x / max(plot_width, 1)

        ny_pos = y / max(plot_height, 1)

        nw = width / max(plot_width, 1)

        nh = height / max(plot_height, 1)

        na = area / total_area

        aspect = width / max(height, 1)

        compactness = min(

            width,
            height

        ) / max(

            width,
            height,
            1
        )

        exterior_touch = float(

            nx_pos < 0.05
            or
            nx_pos > 0.95
            or
            ny_pos < 0.05
            or
            ny_pos > 0.95
        )

        corner_room = float(

            (
                nx_pos < 0.15
                or
                nx_pos > 0.85
            )
            and
            (
                ny_pos < 0.15
                or
                ny_pos > 0.85
            )
        )

        distance_from_entrance = (

            abs(nx_pos - 0.5)
            +
            abs(ny_pos - 0.0)

        ) / 2.0

        ventilation_score = exterior_touch

        sunlight_score = 1.0 - ny_pos

        frontage_score = (
            1.0 - distance_from_entrance
        )

        wet_wall_score = float(

            room_type in [

                "kitchen",
                "bathroom",
                "wash_area"
            ]
        )

        north = 1.0 - ny_pos

        south = ny_pos

        east = nx_pos

        west = 1.0 - nx_pos

        north_east = north * east

        north_west = north * west

        south_east = south * east

        south_west = south * west

        near_window = float(
            exterior_touch
        )

        near_garden = float(

            room_type in [

                "garden",
                "balcony"
            ]
        )

        deg = degree_cent.get(
            room_name,
            0.0
        )

        bet = between_cent.get(
            room_name,
            0.0
        )

        privacy_depth = float(

            room_type in [

                "bedroom",
                "master_bedroom"
            ]
        )

        circulation_distance = deg

        feat = [

            nx_pos,
            ny_pos,

            nw,
            nh,

            na,

            aspect,

            compactness,

            exterior_touch,
            corner_room,

            distance_from_entrance,
            ventilation_score,
            sunlight_score,
            frontage_score,
            wet_wall_score,

            north,
            south,
            east,
            west,

            north_east,
            north_west,
            south_east,
            south_west,

            near_window,
            near_garden,

            deg,
            bet,
            privacy_depth,
            circulation_distance
        ]

        features.append(feat)

    return torch.tensor(

        features,

        dtype=torch.float
    )

# =============================================================================
# GRAPH
# =============================================================================

def build_graph(

    rooms,

    adjacency_pairs,

    plot_width,

    plot_height
):

    x = build_node_features(

        rooms,

        adjacency_pairs,

        plot_width,

        plot_height
    )

    room_index = {}

    for idx, room in enumerate(rooms):

        room_index[
            room["name"]
        ] = idx

    edge_index = []

    edge_attr = []

    for a, b in adjacency_pairs:

        if a not in room_index:
            continue

        if b not in room_index:
            continue

        ia = room_index[a]
        ib = room_index[b]

        edge_index.append([ia, ib])
        edge_index.append([ib, ia])

        ra = rooms[ia]
        rb = rooms[ib]

        dx = abs(
            ra["x"] - rb["x"]
        )

        dy = abs(
            ra["y"] - rb["y"]
        )

        dist = (

            (dx ** 2)
            +
            (dy ** 2)

        ) ** 0.5

        # =====================================================================
        # EDGE FEATURES
        # =====================================================================

        shared_wall = max(

            0.0,

            1.0 - (
                dist
                /
                max(
                    plot_width,
                    plot_height,
                    1
                )
            )
        )

        visibility = 1.0

        doorway = float(
            dist < 25
        )

        plumbing = float(

            ra["type"] in [

                "kitchen",
                "bathroom",
                "wash_area"
            ]
            and
            rb["type"] in [

                "kitchen",
                "bathroom",
                "wash_area"
            ]
        )

        circulation = float(

            ra["type"] in [

                "living",
                "corridor",
                "staircase"
            ]
            or
            rb["type"] in [

                "living",
                "corridor",
                "staircase"
            ]
        )

        hierarchy = float(

            ra["type"] == "living"
            or
            rb["type"] == "living"
        )

        feat = [

            shared_wall,

            dist / max(
                plot_width,
                plot_height,
                1
            ),

            visibility,

            doorway,

            plumbing,

            circulation,

            hierarchy
        ]

        edge_attr.append(feat)
        edge_attr.append(feat)

    # =====================================================================
    # EMPTY GRAPH SAFETY
    # =====================================================================

    if len(edge_index) == 0:

        edge_index = [[0, 0]]

        edge_attr = [[0.0] * 7]

    edge_index = torch.tensor(

        edge_index,

        dtype=torch.long

    ).t().contiguous()

    edge_attr = torch.tensor(

        edge_attr,

        dtype=torch.float
    )

    return Data(

        x=x,

        edge_index=edge_index,

        edge_attr=edge_attr
    )

# =============================================================================
# FALLBACK
# =============================================================================

def heuristic_zoning(rooms):

    print("\n⚠ USING HEURISTIC SEMANTIC ZONING")

    results = {}

    for room in rooms:

        room_type = room["type"]

        if room_type in [

            "living",
            "dining"

        ]:

            zone = "social"
            privacy = "public"
            circulation = "high"
            frontage = "high"
            priority = 0.90

        elif room_type in [

            "kitchen",
            "wash_area",
            "store",
            "bathroom"

        ]:

            zone = "service"
            privacy = "semi_private"
            circulation = "medium"
            frontage = "medium"
            priority = 0.80

        elif "bedroom" in room_type:

            zone = "private"
            privacy = "private"
            circulation = "low"
            frontage = "medium"
            priority = 0.75

        else:

            zone = "semi_private"
            privacy = "semi_private"
            circulation = "medium"
            frontage = "low"
            priority = 0.5

        results[room["name"]] = {

            "zone": zone,

            "privacy": privacy,

            "circulation": circulation,

            "frontage": frontage,

            "semantic_priority": priority
        }

    return results

# =============================================================================
# PREDICT
# =============================================================================

def predict_zones(

    rooms,

    adjacency_pairs,

    plot_width,

    plot_height
):

    model = load_model()

    if model is None:

        return heuristic_zoning(
            rooms
        )

    try:

        graph = build_graph(

            rooms,

            adjacency_pairs,

            plot_width,

            plot_height
        )

        graph = graph.to(DEVICE)

        with torch.no_grad():

            outputs = model(graph)

        zone_pred = outputs[
            "zone"
        ].argmax(dim=1)

        privacy_pred = outputs[
            "privacy"
        ].argmax(dim=1)

        circulation_pred = outputs[
            "circulation"
        ].argmax(dim=1)

        frontage_pred = outputs[
            "frontage"
        ].argmax(dim=1)

        results = {}

        for idx, room in enumerate(rooms):

            zone = ZONE_LABELS.get(

                zone_pred[idx].item(),

                "private"
            )

            privacy = PRIVACY_LABELS.get(

                privacy_pred[idx].item(),

                "semi_private"
            )

            circulation = CIRCULATION_LABELS.get(

                circulation_pred[idx].item(),

                "medium"
            )

            frontage = FRONTAGE_LABELS.get(

                frontage_pred[idx].item(),

                "medium"
            )

            confidence = torch.softmax(

                outputs["zone"][idx],

                dim=0

            ).max().item()

            results[room["name"]] = {

                "zone": zone,

                "privacy": privacy,

                "circulation": circulation,

                "frontage": frontage,

                "semantic_priority": round(
                    confidence,
                    3
                )
            }

        print("\n✔ GNN semantic inference successful")

        return results

    except Exception as e:

        print("\n⚠ GNN inference failed")

        print(e)

        return heuristic_zoning(
            rooms
        )