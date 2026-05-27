# # =============================================================================
# # CONFIG
# # =============================================================================

# import torch

# DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# DATASET_PATH = (
#     r"C:\Users\jyoth\Desktop\Major-Project\Backend"
#     r"\datasets\processed\Layout\resplan_semantic_graph_v6.json"
# )

# CHECKPOINT_DIR = "./checkpoints"

# # =============================================================================
# # FEATURES
# # =============================================================================

# NUM_NODE_FEATURES = 28

# NUM_EDGE_FEATURES = 7

# # =============================================================================
# # CLASSES
# # =============================================================================

# NUM_ROOM_CLASSES = 9

# NUM_ZONE_CLASSES = 4

# # =============================================================================
# # MODEL
# # =============================================================================

# HIDDEN_DIM = 128

# NUM_HEADS = 4

# NUM_LAYERS = 4

# DROPOUT = 0.25

# # =============================================================================
# # TRAINING
# # =============================================================================

# BATCH_SIZE = 32

# EPOCHS = 90

# LEARNING_RATE = 1e-3

# WEIGHT_DECAY = 1e-4

# GRAD_CLIP = 1.0

# =============================================================================
# CONFIG
# =============================================================================

import os
import torch

# =============================================================================
# DEVICE
# =============================================================================

DEVICE = (
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)

# =============================================================================
# ROOT PATHS
# =============================================================================

BASE_DIR = (
    r"C:\Users\jyoth\Desktop\Major-Project\Backend"
)

DATASET_PATH = os.path.join(

    BASE_DIR,

    "datasets",
    "processed",
    "Layout",

    "resplan_semantic_graph_v6.json"
)

CHECKPOINT_DIR = os.path.join(

    BASE_DIR,

    "models",
    "Layout",
    "Graph_model",

    "checkpoints"
)

CHECKPOINT_PATH = os.path.join(

    CHECKPOINT_DIR,

    "semantic_topology_gnn_v2.pt"
)

# =============================================================================
# FEATURES
# =============================================================================

NUM_NODE_FEATURES = 28

NUM_EDGE_FEATURES = 7

# =============================================================================
# CLASSES
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

ZONE_LABELS = {

    "social": 0,
    "private": 1,
    "service": 2,
    "exterior": 3
}

NUM_ROOM_CLASSES = len(
    ROOM_LABELS
)

NUM_ZONE_CLASSES = len(
    ZONE_LABELS
)

NUM_PRIVACY_CLASSES = 3

NUM_CIRCULATION_CLASSES = 3

NUM_FRONTAGE_CLASSES = 3

# =============================================================================
# MODEL
# =============================================================================

HIDDEN_DIM = 128

NUM_HEADS = 4

NUM_LAYERS = 4

DROPOUT = 0.25

USE_RESIDUAL = True

USE_EDGE_ATTR = True

# =============================================================================
# TRAINING
# =============================================================================

BATCH_SIZE = 32

EPOCHS = 90

LEARNING_RATE = 1e-3

WEIGHT_DECAY = 1e-4

GRAD_CLIP = 1.0

NUM_WORKERS = 0

# =============================================================================
# LOSS WEIGHTS
# =============================================================================

ROOM_LOSS_WEIGHT = 1.0

ZONE_LOSS_WEIGHT = 0.5

PRIVACY_LOSS_WEIGHT = 0.4

CIRCULATION_LOSS_WEIGHT = 0.4

FRONTAGE_LOSS_WEIGHT = 0.3

ADJACENCY_LOSS_WEIGHT = 0.8

# =============================================================================
# RULE GUIDED LOSS
# =============================================================================

RULE_PENALTY_WEIGHT = 0.25

# =============================================================================
# TRAIN / VAL SPLIT
# =============================================================================

TRAIN_SPLIT = 0.8

VAL_SPLIT = 0.1

TEST_SPLIT = 0.1

# =============================================================================
# RANDOMNESS
# =============================================================================

SEED = 42

torch.manual_seed(SEED)

if torch.cuda.is_available():

    torch.cuda.manual_seed_all(SEED)

# =============================================================================
# DEBUG
# =============================================================================

DEBUG = False