# =============================================================================
# DATASET
# =============================================================================

import json
import torch

from torch_geometric.data import Data
from torch.utils.data import Dataset

from config import *

class ResPlanGraphDataset(Dataset):

    def __init__(self):

        with open(DATASET_PATH, "r") as f:

            self.graphs = json.load(f)

    def __len__(self):

        return len(self.graphs)

    def __getitem__(self, idx):

        g = self.graphs[idx]

        data = Data(

            x=torch.tensor(
                g["x"],
                dtype=torch.float
            ),

            edge_index=torch.tensor(
                g["edge_index"],
                dtype=torch.long
            ).t().contiguous(),

            edge_attr=torch.tensor(
                g["edge_attr"],
                dtype=torch.float
            ),

            room_labels=torch.tensor(
                g["room_labels"],
                dtype=torch.long
            ),

            zone_labels=torch.tensor(
                g["zone_labels"],
                dtype=torch.long
            ),

            privacy_labels=torch.tensor(
                g["privacy_labels"],
                dtype=torch.long
            ),

            circulation_labels=torch.tensor(
                g["circulation_labels"],
                dtype=torch.long
            ),

            frontage_labels=torch.tensor(
                g["frontage_labels"],
                dtype=torch.long
            ),

            adjacency_targets=torch.tensor(
                g["adjacency_targets"],
                dtype=torch.float
            )
        )

        return data