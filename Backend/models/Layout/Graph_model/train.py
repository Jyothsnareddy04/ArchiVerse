# =============================================================================
# TRAINER
# =============================================================================

import os
import torch
import torch.nn.functional as F

from tqdm import tqdm

from sklearn.model_selection import (
    train_test_split
)

from torch_geometric.loader import (
    DataLoader
)

from dataset import ResPlanGraphDataset

from model import SemanticGNN

from config import *

# =============================================================================
# DATASET
# =============================================================================

dataset = ResPlanGraphDataset()

train_idx, val_idx = train_test_split(

    list(range(len(dataset))),

    test_size=0.1,

    random_state=42
)

train_dataset = torch.utils.data.Subset(
    dataset,
    train_idx
)

val_dataset = torch.utils.data.Subset(
    dataset,
    val_idx
)

train_loader = DataLoader(

    train_dataset,

    batch_size=BATCH_SIZE,

    shuffle=True
)

val_loader = DataLoader(

    val_dataset,

    batch_size=BATCH_SIZE,

    shuffle=False
)

# =============================================================================
# MODEL
# =============================================================================

model = SemanticGNN().to(DEVICE)

optimizer = torch.optim.AdamW(

    model.parameters(),

    lr=LEARNING_RATE,

    weight_decay=WEIGHT_DECAY
)

# =============================================================================
# ROOM WEIGHTS
# =============================================================================

room_weights = torch.tensor([

    1.0,
    1.3,
    1.0,
    1.0,
    1.5,
    4.0,
    5.0,
    8.0,
    6.0

]).to(DEVICE)

# =============================================================================
# SAVE
# =============================================================================

os.makedirs(
    CHECKPOINT_DIR,
    exist_ok=True
)

best_acc = 0

# =============================================================================
# TRAIN LOOP
# =============================================================================

for epoch in range(EPOCHS):

    model.train()

    total_correct = 0
    total_nodes = 0

    loop = tqdm(train_loader)

    for batch in loop:

        batch = batch.to(DEVICE)

        optimizer.zero_grad()

        outputs = model(batch)

        # =====================================================================
        # NODE LOSSES
        # =====================================================================

        room_loss = F.cross_entropy(

            outputs["room"],

            batch.room_labels,

            weight=room_weights
        )

        zone_loss = F.cross_entropy(

            outputs["zone"],

            batch.zone_labels
        )

        privacy_loss = F.cross_entropy(

            outputs["privacy"],

            batch.privacy_labels
        )

        circulation_loss = F.cross_entropy(

            outputs["circulation"],

            batch.circulation_labels
        )

        frontage_loss = F.cross_entropy(

            outputs["frontage"],

            batch.frontage_labels
        )

        # =====================================================================
        # EDGE LOSS
        # =====================================================================

        adjacency_loss = F.mse_loss(

            outputs["adjacency"],

            batch.adjacency_targets
        )

        # =====================================================================
        # RULE GUIDED LOSS
        # =====================================================================

        room_preds = outputs[
            "room"
        ].argmax(dim=1)

        zone_preds = outputs[
            "zone"
        ].argmax(dim=1)

        rule_penalty = 0.0

        # bathroom cannot be social

        bathroom_nodes = (
            room_preds == 3
        )

        social_zone = (
            zone_preds == 0
        )

        violation = (
            bathroom_nodes & social_zone
        ).float()

        rule_penalty += (
            violation.mean()
        )

        # =====================================================================
        # TOTAL LOSS
        # =====================================================================

        loss = (

            room_loss +

            0.5 * zone_loss +

            0.3 * privacy_loss +

            0.3 * circulation_loss +

            0.3 * frontage_loss +

            0.5 * adjacency_loss +

            0.2 * rule_penalty
        )

        # =====================================================================
        # BACKPROP
        # =====================================================================

        loss.backward()

        torch.nn.utils.clip_grad_norm_(

            model.parameters(),

            GRAD_CLIP
        )

        optimizer.step()

        # =====================================================================
        # ACC
        # =====================================================================

        preds = outputs[
            "room"
        ].argmax(dim=1)

        correct = (
            preds == batch.room_labels
        ).sum().item()

        total_correct += correct

        total_nodes += (
            batch.room_labels.size(0)
        )

        acc = (
            total_correct / total_nodes
        )

        loop.set_description(
            f"Epoch {epoch+1}"
        )

        loop.set_postfix(
            loss=loss.item(),
            acc=acc
        )

    # =========================================================================
    # VALIDATION
    # =========================================================================

    model.eval()

    val_correct = 0
    val_nodes = 0

    with torch.no_grad():

        for batch in val_loader:

            batch = batch.to(DEVICE)

            outputs = model(batch)

            preds = outputs[
                "room"
            ].argmax(dim=1)

            val_correct += (

                preds == batch.room_labels

            ).sum().item()

            val_nodes += (
                batch.room_labels.size(0)
            )

    val_acc = val_correct / val_nodes

    print(
        f"\nVAL ACC: {val_acc:.4f}"
    )

    # =========================================================================
    # SAVE
    # =========================================================================

    if val_acc > best_acc:

        best_acc = val_acc

        torch.save({

            "model_state_dict":
            model.state_dict(),

            "val_acc":
            val_acc

        },

        os.path.join(

            CHECKPOINT_DIR,

            "semantic_topology_gnn_v2.pt"
        ))

        print(
            f"\nBEST MODEL SAVED "
            f"{val_acc:.4f}"
        )