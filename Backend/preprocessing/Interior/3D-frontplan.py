# ============================================================
# 3D-FRONT DATASET PREPROCESSOR (FINAL CLEAN VERSION)
# ============================================================
#
# PURPOSE:
# Convert raw 3D-FRONT scenes into:
#
# 1. Clean room-wise furniture graphs
# 2. GNN-ready adjacency data
# 3. Furniture placement coordinates
# 4. Semantic room metadata
#
# OUTPUT:
# C:\Users\jyoth\Desktop\Major-Project\Backend\datasets\processed\Interior
#
# ============================================================

import os
import json
import math
from pathlib import Path

# ============================================================
# PATHS
# ============================================================

RAW_DATASET_PATH = r"C:\Users\jyoth\Desktop\Major-Project\Backend\datasets\raw\Interior\3D-FRONT"

PROCESSED_PATH = r"C:\Users\jyoth\Desktop\Major-Project\Backend\datasets\processed\Interior\dataset"

os.makedirs(PROCESSED_PATH, exist_ok=True)

# ============================================================
# VALID FURNITURE FILTERS
# ============================================================

INVALID_CATEGORIES = [

    "window",
    "door",
    "ceiling",
    "wall",
    "floor",
    "beam",
    "column",
    "roof",
    "stairs",
    "railing",
    "curtain",
    "baseboard",
    "switch",
    "socket"
]

# ============================================================
# DISTANCE FUNCTION
# ============================================================

def euclidean_distance(a, b):

    return math.sqrt(
        (a[0] - b[0]) ** 2 +
        (a[1] - b[1]) ** 2 +
        (a[2] - b[2]) ** 2
    )

# ============================================================
# NORMALIZE ROOM TYPES
# ============================================================

def normalize_room_type(room_type):

    room_type = room_type.lower()

    if "bed" in room_type:
        return "bedroom"

    if "living" in room_type:
        return "living_room"

    if "kitchen" in room_type:
        return "kitchen"

    if "bath" in room_type:
        return "bathroom"

    if "dining" in room_type:
        return "dining_room"

    if "study" in room_type:
        return "study"

    if "office" in room_type:
        return "office"

    return "unknown"

# ============================================================
# FILTER FURNITURE
# ============================================================

def is_valid_furniture(category):

    category = category.lower()

    for invalid in INVALID_CATEGORIES:

        if invalid in category:
            return False

    return True

# ============================================================
# EXTRACT FURNITURE
# ============================================================

def extract_furniture(scene_data):

    furniture_map = {}

    furniture_list = scene_data.get("furniture", [])

    for item in furniture_list:

        uid = item.get("uid", "")

        category = item.get(
            "title",
            item.get("sourceCategoryId", "unknown")
        )

        # ----------------------------------------------------
        # FILTER INVALID OBJECTS
        # ----------------------------------------------------

        if not is_valid_furniture(category):
            continue

        furniture_map[uid] = {

            "uid": uid,

            "jid": item.get("jid", ""),

            "bbox": item.get("bbox", []),

            "size": item.get("size", []),

            "category": category,

            "valid": item.get("valid", True)
        }

    return furniture_map

# ============================================================
# EXTRACT ROOMS
# ============================================================

def extract_rooms(scene_data):

    rooms = []

    scene = scene_data.get("scene", {})

    room_list = scene.get("room", [])

    for room in room_list:

        room_type = normalize_room_type(
            room.get("type", "unknown")
        )

        # ----------------------------------------------------
        # REMOVE UNKNOWN ROOMS
        # ----------------------------------------------------

        if room_type == "unknown":
            continue

        room_id = room.get(
            "instanceid",
            room.get("uid", "")
        )

        children = room.get("children", [])

        if len(children) == 0:
            continue

        rooms.append({

            "room_id": room_id,

            "room_type": room_type,

            "children": children
        })

    return rooms

# ============================================================
# BUILD ROOM GRAPH
# ============================================================

def build_room_graph(room, furniture_map):

    furniture_nodes = []

    children = room.get("children", [])

    for child in children:

        ref = child.get("ref") or child.get("instanceid")

        if ref not in furniture_map:
            continue

        furniture = furniture_map[ref]

        if furniture["valid"] is False:
            continue

        position = child.get("pos", [0, 0, 0])

        rotation = child.get("rot", [0, 0, 0])

        scale = child.get("scale", [1, 1, 1])

        node = {

            "category": furniture["category"],

            "position": position,

            "rotation": rotation,

            "scale": scale,

            "bbox": furniture["bbox"],

            "size": furniture["size"]
        }

        furniture_nodes.append(node)

    # --------------------------------------------------------
    # REMOVE EMPTY ROOMS
    # --------------------------------------------------------

    if len(furniture_nodes) == 0:
        return None

    # ========================================================
    # BUILD ADJACENCY EDGES
    # ========================================================

    edges = []

    for i in range(len(furniture_nodes)):

        for j in range(i + 1, len(furniture_nodes)):

            p1 = furniture_nodes[i]["position"]

            p2 = furniture_nodes[j]["position"]

            dist = euclidean_distance(p1, p2)

            if dist <= 4.0:

                edges.append({

                    "source": i,

                    "target": j,

                    "distance": round(dist, 3)
                })

    return {

        "room_id": room["room_id"],

        "room_type": room["room_type"],

        "furniture": furniture_nodes,

        "edges": edges
    }

# ============================================================
# PROCESS SINGLE SCENE
# ============================================================

def process_scene(scene_path):

    try:

        with open(scene_path, "r", encoding="utf-8") as f:

            scene_json = json.load(f)

        furniture_map = extract_furniture(scene_json)

        rooms = extract_rooms(scene_json)

        processed_rooms = []

        for room in rooms:

            graph = build_room_graph(
                room,
                furniture_map
            )

            if graph is None:
                continue

            processed_rooms.append(graph)

        return processed_rooms

    except Exception as e:

        print(f"\n[ERROR] {scene_path}")
        print(e)

        return []

# ============================================================
# SAVE ROOM FILE
# ============================================================

def save_room(room_data, scene_name, room_index):

    room_type = room_data["room_type"]

    output_name = f"{scene_name}_{room_type}_{room_index}.json"

    output_path = os.path.join(
        PROCESSED_PATH,
        output_name
    )

    with open(output_path, "w", encoding="utf-8") as f:

        json.dump(room_data, f, indent=4)

# ============================================================
# MAIN PREPROCESSING
# ============================================================

def preprocess_dataset():

    json_files = []

    for root, dirs, files in os.walk(RAW_DATASET_PATH):

        for file in files:

            if file.endswith(".json"):

                json_files.append(
                    os.path.join(root, file)
                )

    print("\n===================================")
    print(f"FOUND {len(json_files)} JSON FILES")
    print("===================================\n")

    total_rooms = 0

    for idx, file_path in enumerate(json_files):

        print(f"[{idx+1}/{len(json_files)}] Processing")

        scene_name = Path(file_path).stem

        processed_rooms = process_scene(file_path)

        for i, room_data in enumerate(processed_rooms):

            save_room(
                room_data,
                scene_name,
                i
            )

            total_rooms += 1

    print("\n===================================")
    print(" PREPROCESSING COMPLETE")
    print("===================================")
    print(f"TOTAL ROOMS SAVED : {total_rooms}")
    print(f"OUTPUT PATH       : {PROCESSED_PATH}")
    print("===================================\n")

# ============================================================
# ENTRY
# ============================================================

if __name__ == "__main__":

    preprocess_dataset()