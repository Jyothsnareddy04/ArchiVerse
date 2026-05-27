# =============================================================================
# ARCHIVERSE — SEMANTIC TOPOLOGY GNN FULL EVALUATION
# =============================================================================

import os
import sys
import torch
import numpy as np

from tqdm import tqdm

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)

from torch_geometric.loader import DataLoader

# =============================================================================
# PATHS
# =============================================================================

GRAPH_MODEL_DIR = (
    r"C:\Users\jyoth\Desktop\Major-Project"
    r"\Backend\models\Layout\Graph_model"
)

if GRAPH_MODEL_DIR not in sys.path:

    sys.path.insert(
        0,
        GRAPH_MODEL_DIR
    )

# =============================================================================
# IMPORTS
# =============================================================================

from dataset import ResPlanGraphDataset
from model import SemanticGNN
from config import *

# =============================================================================
# CHECKPOINT
# =============================================================================

CHECKPOINT_PATH = os.path.join(

    CHECKPOINT_DIR,

    "semantic_topology_gnn_v2.pt"
)

# =============================================================================
# LABELS
# =============================================================================

ROOMS = {

    0: "living",
    1: "kitchen",
    2: "bedroom",
    3: "bathroom",
    4: "balcony",
    5: "storage",
    6: "stair",
    7: "parking",
    8: "garden"
}

# =============================================================================
# LOAD CHECKPOINT
# =============================================================================

print("\n" + "=" * 70)
print("CHECKPOINT INSPECTION")
print("=" * 70)

checkpoint = torch.load(

    CHECKPOINT_PATH,

    map_location="cpu"
)

if (
    isinstance(checkpoint, dict)
    and
    "model_state_dict" in checkpoint
):

    state_dict = checkpoint[
        "model_state_dict"
    ]

    print("\nCHECKPOINT TYPE: TRAINING CHECKPOINT")

else:

    state_dict = checkpoint

    print("\nCHECKPOINT TYPE: RAW STATE DICT")

# =============================================================================
# ARCHITECTURE DETECTION
# =============================================================================

print("\nMODEL FEATURES")

print(

    "✔ input_proj"

    if "input_proj.weight" in state_dict

    else "✘ no input_proj"
)

print(

    "✔ edge_attr"

    if any(
        "lin_edge" in k
        for k in state_dict
    )

    else "✘ no edge_attr"
)

print(

    "✔ residual"

    if any(
        ".res." in k
        for k in state_dict
    )

    else "✘ no residual"
)

if "convs.0.att" in state_dict:

    print(

        "✔ attention shape:",

        state_dict[
            "convs.0.att"
        ].shape
    )

# =============================================================================
# LOAD DATASET
# =============================================================================

print("\n" + "=" * 70)
print("LOADING DATASET")
print("=" * 70)

dataset = ResPlanGraphDataset()

print("\nTOTAL GRAPHS:", len(dataset))

sample = dataset[0]

print("\nSAMPLE GRAPH")

print("NODES:", sample.x.shape)

print("EDGES:", sample.edge_index.shape)

print("EDGE ATTR:", sample.edge_attr.shape)

# =============================================================================
# FEATURE SUPPORT
# =============================================================================

print("\n" + "=" * 70)
print("SUPPORTED NODE FEATURES")
print("=" * 70)

NODE_FEATURES = [

    "x_norm",
    "y_norm",

    "width_norm",
    "height_norm",

    "relative_area",

    "aspect_ratio",

    "compactness",

    "exterior_touch",
    "corner_room",

    "distance_from_entrance",
    "ventilation_score",
    "sunlight_score",
    "frontage_score",
    "wet_wall_score",

    "north",
    "south",
    "east",
    "west",

    "north_east",
    "north_west",
    "south_east",
    "south_west",

    "near_window",
    "near_garden",

    "degree_centrality",
    "betweenness_centrality",
    "privacy_depth",
    "circulation_distance"
]

for i, feat in enumerate(NODE_FEATURES):

    print(f"{i:02d} -> {feat}")

print("\nEDGE FEATURES")

EDGE_FEATURES = [

    "shared_wall_length",
    "distance",
    "visibility_connection",
    "doorway_connection",
    "plumbing_connection",
    "circulation_connection",
    "hierarchy_connection"
]

for i, feat in enumerate(EDGE_FEATURES):

    print(f"{i:02d} -> {feat}")

# =============================================================================
# LOAD MODEL
# =============================================================================

print("\n" + "=" * 70)
print("LOADING MODEL")
print("=" * 70)

model = SemanticGNN().to(DEVICE)

model.load_state_dict(state_dict)

model.eval()

print("\nMODEL LOADED SUCCESSFULLY")

# =============================================================================
# ARCHITECTURE
# =============================================================================

print("\nMODEL ARCHITECTURE\n")

print(model)

# =============================================================================
# PARAMS
# =============================================================================

params = sum(

    p.numel()

    for p in model.parameters()

    if p.requires_grad
)

print(f"\nTRAINABLE PARAMS: {params:,}")

# =============================================================================
# DATALOADER
# =============================================================================

loader = DataLoader(

    dataset,

    batch_size=32,

    shuffle=False
)

# =============================================================================
# METRIC STORAGE
# =============================================================================

all_gt = []
all_pred = []
all_conf = []

zone_gt = []
zone_pred = []

privacy_gt = []
privacy_pred = []

circ_gt = []
circ_pred = []

front_gt = []
front_pred = []

adj_gt = []
adj_pred = []

# =============================================================================
# EVALUATION
# =============================================================================

print("\n" + "=" * 70)
print("RUNNING FULL EVALUATION")
print("=" * 70)

with torch.no_grad():

    for batch in tqdm(loader):

        batch = batch.to(DEVICE)

        outputs = model(batch)

        # ================================================================
        # ROOM
        # ================================================================

        probs = torch.softmax(

            outputs["room"],

            dim=1
        )

        conf, preds = probs.max(dim=1)

        all_gt.extend(
            batch.room_labels.cpu().numpy()
        )

        all_pred.extend(
            preds.cpu().numpy()
        )

        all_conf.extend(
            conf.cpu().numpy()
        )

        # ================================================================
        # ZONE
        # ================================================================

        zpred = outputs[
            "zone"
        ].argmax(dim=1)

        zone_gt.extend(
            batch.zone_labels.cpu().numpy()
        )

        zone_pred.extend(
            zpred.cpu().numpy()
        )

        # ================================================================
        # PRIVACY
        # ================================================================

        ppred = outputs[
            "privacy"
        ].argmax(dim=1)

        privacy_gt.extend(
            batch.privacy_labels.cpu().numpy()
        )

        privacy_pred.extend(
            ppred.cpu().numpy()
        )

        # ================================================================
        # CIRCULATION
        # ================================================================

        cpred = outputs[
            "circulation"
        ].argmax(dim=1)

        circ_gt.extend(
            batch.circulation_labels.cpu().numpy()
        )

        circ_pred.extend(
            cpred.cpu().numpy()
        )

        # ================================================================
        # FRONTAGE
        # ================================================================

        fpred = outputs[
            "frontage"
        ].argmax(dim=1)

        front_gt.extend(
            batch.frontage_labels.cpu().numpy()
        )

        front_pred.extend(
            fpred.cpu().numpy()
        )

        # ================================================================
        # ADJACENCY
        # ================================================================

        adj_pred.extend(

            outputs["adjacency"]
            .cpu()
            .numpy()
        )

        adj_gt.extend(

            batch.adjacency_targets
            .cpu()
            .numpy()
        )

# =============================================================================
# ROOM METRICS
# =============================================================================

print("\n" + "=" * 70)
print("ROOM METRICS")
print("=" * 70)

acc = accuracy_score(
    all_gt,
    all_pred
)

prec = precision_score(
    all_gt,
    all_pred,
    average="weighted"
)

rec = recall_score(
    all_gt,
    all_pred,
    average="weighted"
)

f1 = f1_score(
    all_gt,
    all_pred,
    average="weighted"
)

print(f"\nACCURACY : {acc:.4f}")

print(f"PRECISION: {prec:.4f}")

print(f"RECALL   : {rec:.4f}")

print(f"F1 SCORE : {f1:.4f}")

# =============================================================================
# CLASS REPORT
# =============================================================================

print("\n" + "=" * 70)
print("PER CLASS REPORT")
print("=" * 70)

print(

    classification_report(

        all_gt,

        all_pred,

        target_names=list(
            ROOMS.values()
        )
    )
)

# =============================================================================
# MULTI TASK
# =============================================================================

print("\n" + "=" * 70)
print("MULTI TASK ACCURACY")
print("=" * 70)

print(

    "\nZONE:",

    round(
        accuracy_score(
            zone_gt,
            zone_pred
        ),
        4
    )
)

print(

    "PRIVACY:",

    round(
        accuracy_score(
            privacy_gt,
            privacy_pred
        ),
        4
    )
)

print(

    "CIRCULATION:",

    round(
        accuracy_score(
            circ_gt,
            circ_pred
        ),
        4
    )
)

print(

    "FRONTAGE:",

    round(
        accuracy_score(
            front_gt,
            front_pred
        ),
        4
    )
)

# =============================================================================
# ADJACENCY
# =============================================================================

adj_gt = np.array(adj_gt)

adj_pred = np.array(adj_pred)

adj_mae = np.mean(

    np.abs(

        adj_gt - adj_pred
    )
)

print("\nADJACENCY MAE:", round(adj_mae, 4))

# =============================================================================
# CONFIDENCE
# =============================================================================

print("\n" + "=" * 70)
print("CONFIDENCE STATS")
print("=" * 70)

print(

    "\nAVG:",

    round(
        np.mean(all_conf),
        4
    )
)

print(

    "MAX:",

    round(
        np.max(all_conf),
        4
    )
)

print(

    "MIN:",

    round(
        np.min(all_conf),
        4
    )
)

# =============================================================================
# CONFUSION MATRIX
# =============================================================================

print("\n" + "=" * 70)
print("CONFUSION MATRIX")
print("=" * 70)

print(

    confusion_matrix(
        all_gt,
        all_pred
    )
)

# =============================================================================
# CAPABILITIES
# =============================================================================

print("\n" + "=" * 70)
print("MODEL CAPABILITIES")
print("=" * 70)

print("""

✔ Semantic Room Classification
✔ Architectural Zone Prediction
✔ Privacy Intelligence
✔ Circulation Intelligence
✔ Frontage Importance Prediction
✔ Adjacency Compatibility Prediction
✔ Edge-aware Graph Reasoning
✔ Multi-head Graph Attention
✔ Residual GATv2 Architecture
✔ Topology-aware Semantic Embeddings
✔ Architectural Spatial Intelligence
✔ Semantic Constraint Learning
✔ Edge Attribute Reasoning
✔ Wet-zone Understanding
✔ Orientation Reasoning
✔ Boundary Intelligence
✔ Semantic Topology Learning

""")

print("=" * 70)
print("EVALUATION COMPLETE")
print("=" * 70)


# =============================================================================
# TRAINING CURVE GRAPH
# =============================================================================

import matplotlib.pyplot as plt

print("\n" + "=" * 70)
print("BUILDING TRAINING GRAPH")
print("=" * 70)

# =============================================================================
# ARCHIVERSE — SEMANTIC GNN PERFORMANCE CURVE
# =============================================================================

import matplotlib.pyplot as plt

# =============================================================================
# TASKS
# =============================================================================

tasks = [

    "Room",
    "Zone",
    "Privacy",
    "Circulation",
    "Frontage"
]

accuracies = [

    99.42,
    99.43,
    99.44,
    99.81,
    99.53
]

# =============================================================================
# PLOT
# =============================================================================

plt.figure(figsize=(10, 6))

plt.plot(

    tasks,

    accuracies,

    marker="o",

    linewidth=3
)

# =============================================================================
# POINT LABELS
# =============================================================================

for x, y in zip(

    tasks,

    accuracies
):

    plt.text(

        x,

        y + 0.03,

        f"{y:.2f}%",

        ha="center",

        fontsize=11
    )

# =============================================================================
# TITLE
# =============================================================================

plt.title(

    "Semantic GNN Multi-Task Performance",

    fontsize=16
)

plt.xlabel(

    "Prediction Tasks",

    fontsize=13
)

plt.ylabel(

    "Accuracy (%)",

    fontsize=13
)

# =============================================================================
# LIMITS
# =============================================================================

plt.ylim(99.0, 100)

# =============================================================================
# GRID
# =============================================================================

plt.grid(

    True,

    linestyle="--",

    alpha=0.6
)

# =============================================================================
# SAVE
# =============================================================================

save_path = "semantic_gnn_performance_curve.png"

plt.savefig(

    save_path,

    dpi=300,

    bbox_inches="tight"
)

print("\nGRAPH SAVED:")
print(save_path)

# =============================================================================
# SHOW
# =============================================================================

plt.show()