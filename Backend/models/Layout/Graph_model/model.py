# =============================================================================
# SEMANTIC GNN
# =============================================================================

import os
import sys

CURRENT_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

if CURRENT_DIR not in sys.path:

    sys.path.insert(
        0,
        CURRENT_DIR
    )

import torch
import torch.nn as nn
import torch.nn.functional as F

from torch_geometric.nn import (
    GATv2Conv,
    LayerNorm
)
# =============================================================================
# LOAD CONFIG DIRECTLY
# =============================================================================

import importlib.util

CONFIG_PATH = os.path.join(
    CURRENT_DIR,
    "config.py"
)

config_spec = importlib.util.spec_from_file_location(
    "graph_config",
    CONFIG_PATH
)

graph_config = importlib.util.module_from_spec(
    config_spec
)

config_spec.loader.exec_module(
    graph_config
)

# =============================================================================
# CONFIG VARIABLES
# =============================================================================

NUM_NODE_FEATURES = graph_config.NUM_NODE_FEATURES

NUM_EDGE_FEATURES = graph_config.NUM_EDGE_FEATURES

NUM_ROOM_CLASSES = graph_config.NUM_ROOM_CLASSES

NUM_ZONE_CLASSES = graph_config.NUM_ZONE_CLASSES

HIDDEN_DIM = graph_config.HIDDEN_DIM

NUM_HEADS = graph_config.NUM_HEADS

NUM_LAYERS = graph_config.NUM_LAYERS

DROPOUT = graph_config.DROPOUT

print("\nCONFIG IMPORT SUCCESS")

print("NUM_NODE_FEATURES =", NUM_NODE_FEATURES) 


class SemanticGNN(nn.Module):

    def __init__(self):

        super().__init__()

        # =====================================================================
        # INPUT PROJECTION
        # =====================================================================

        self.input_proj = nn.Linear(
            NUM_NODE_FEATURES,
            HIDDEN_DIM
        )

        # =====================================================================
        # GNN LAYERS
        # =====================================================================

        self.convs = nn.ModuleList()

        self.norms = nn.ModuleList()

        for _ in range(NUM_LAYERS):

            self.convs.append(

                GATv2Conv(

                    HIDDEN_DIM,

                    HIDDEN_DIM // NUM_HEADS,

                    heads=NUM_HEADS,

                    concat=True,

                    edge_dim=NUM_EDGE_FEATURES,

                    residual=True,

                    dropout=DROPOUT
                )
            )

            self.norms.append(
                LayerNorm(HIDDEN_DIM)
            )

        # =====================================================================
        # NODE HEADS
        # =====================================================================

        self.room_head = nn.Linear(
            HIDDEN_DIM,
            NUM_ROOM_CLASSES
        )

        self.zone_head = nn.Linear(
            HIDDEN_DIM,
            NUM_ZONE_CLASSES
        )

        self.privacy_head = nn.Linear(
            HIDDEN_DIM,
            3
        )

        self.circulation_head = nn.Linear(
            HIDDEN_DIM,
            3
        )

        self.frontage_head = nn.Linear(
            HIDDEN_DIM,
            3
        )

        # =====================================================================
        # EDGE HEAD
        # =====================================================================

        self.adjacency_head = nn.Sequential(

            nn.Linear(
                HIDDEN_DIM * 2,
                128
            ),

            nn.ReLU(),

            nn.Linear(
                128,
                1
            )
        )

    # =========================================================================
    # FORWARD
    # =========================================================================

    def forward(self, data):

        x = data.x.float()

        edge_index = data.edge_index

        edge_attr = data.edge_attr.float()

        # =====================================================================
        # INPUT PROJECTION
        # =====================================================================

        x = self.input_proj(x)

        # =====================================================================
        # GNN
        # =====================================================================

        for conv, norm in zip(

            self.convs,

            self.norms
        ):

            residual = x

            x = conv(
                x,
                edge_index,
                edge_attr
            )

            x = norm(x)

            x = F.elu(x)

            x = x + residual

            x = F.dropout(
                x,
                p=DROPOUT,
                training=self.training
            )

        # =====================================================================
        # NODE OUTPUTS
        # =====================================================================

        room_logits = self.room_head(x)

        zone_logits = self.zone_head(x)

        privacy_logits = self.privacy_head(x)

        circulation_logits = self.circulation_head(x)

        frontage_logits = self.frontage_head(x)

        # =====================================================================
        # EDGE OUTPUTS
        # =====================================================================

        src = edge_index[0]

        dst = edge_index[1]

        edge_embeddings = torch.cat([

            x[src],
            x[dst]

        ], dim=1)

        adjacency_pred = self.adjacency_head(
            edge_embeddings
        ).squeeze(-1)

        return {

            "room": room_logits,

            "zone": zone_logits,

            "privacy": privacy_logits,

            "circulation": circulation_logits,

            "frontage": frontage_logits,

            "adjacency": adjacency_pred
        }