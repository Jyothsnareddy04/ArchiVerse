# ============================================================
# CMP FACADE DATASET PREPROCESSOR
# ============================================================
#
# PURPOSE:
# ------------------------------------------------------------
# Converts CMP Facade dataset into:
#
# 1. Training image pairs
# 2. Semantic segmentation masks
# 3. UNet-ready dataset structure
#
# OUTPUT:
# ------------------------------------------------------------
# datasets/processed/Exterior/
#
# ├── images/
# ├── masks/
# └── metadata/
#
# ============================================================

import os
import cv2
import glob
import json
import shutil
import numpy as np

from tqdm import tqdm
from PIL import Image

# ============================================================
# PATHS
# ============================================================

RAW_PATH = r"C:\Users\jyoth\Desktop\Major-Project\Backend\datasets\raw\Exterior"

BASE_PATH = os.path.join(
    RAW_PATH,
    "base"
)

OUTPUT_PATH = r"C:\Users\jyoth\Desktop\Major-Project\Backend\datasets\processed\Exterior"

IMAGE_OUTPUT = os.path.join(
    OUTPUT_PATH,
    "images"
)

MASK_OUTPUT = os.path.join(
    OUTPUT_PATH,
    "masks"
)

META_OUTPUT = os.path.join(
    OUTPUT_PATH,
    "metadata"
)

# ============================================================
# CREATE FOLDERS
# ============================================================

os.makedirs(IMAGE_OUTPUT, exist_ok=True)
os.makedirs(MASK_OUTPUT, exist_ok=True)
os.makedirs(META_OUTPUT, exist_ok=True)

# ============================================================
# CLEAR OLD FILES
# ============================================================

for folder in [

    IMAGE_OUTPUT,
    MASK_OUTPUT,
    META_OUTPUT
]:

    for file in os.listdir(folder):

        file_path = os.path.join(
            folder,
            file
        )

        if os.path.isfile(file_path):

            os.remove(file_path)

print("\nOLD PROCESSED FILES CLEARED\n")

# ============================================================
# LABEL MAP
# ============================================================

LABEL_MAP = {

    0: "background",
    1: "facade",
    2: "window",
    3: "door",
    4: "cornice",
    5: "sill",
    6: "balcony",
    7: "blind",
    8: "deco",
    9: "molding",
    10: "pillar",
    11: "shop"
}

# ============================================================
# FIND FILES
# ============================================================

jpg_files = sorted(

    glob.glob(
        os.path.join(BASE_PATH, "*.jpg")
    )
)

print("\n===================================")
print(f"TOTAL IMAGES FOUND : {len(jpg_files)}")
print("===================================\n")

# ============================================================
# TARGET IMAGE SIZE
# ============================================================

IMG_SIZE = 512

# ============================================================
# PROCESS DATASET
# ============================================================

processed_count = 0

for img_path in tqdm(jpg_files):

    try:

        file_name = os.path.basename(img_path)

        file_stem = os.path.splitext(
            file_name
        )[0]

        # ----------------------------------------------------
        # MASK PATH
        # ----------------------------------------------------

        mask_path = os.path.join(

            BASE_PATH,

            f"{file_stem}.png"
        )

        if not os.path.exists(mask_path):
            continue

        # ----------------------------------------------------
        # LOAD IMAGE
        # ----------------------------------------------------

        image = cv2.imread(img_path)

        image = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2RGB
        )

        # ----------------------------------------------------
        # LOAD MASK
        # ----------------------------------------------------

        mask = np.array(
            Image.open(mask_path)
        )

        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        if image is None:
            continue

        if mask is None:
            continue

        # ----------------------------------------------------
        # RESIZE
        # ----------------------------------------------------

        image = cv2.resize(

            image,

            (IMG_SIZE, IMG_SIZE),

            interpolation=cv2.INTER_AREA
        )

        mask = cv2.resize(

            mask,

            (IMG_SIZE, IMG_SIZE),

            interpolation=cv2.INTER_NEAREST
        )

        # ----------------------------------------------------
        # SAVE IMAGE
        # ----------------------------------------------------

        output_img = os.path.join(

            IMAGE_OUTPUT,

            f"{file_stem}.png"
        )

        cv2.imwrite(

            output_img,

            cv2.cvtColor(
                image,
                cv2.COLOR_RGB2BGR
            )
        )

        # ----------------------------------------------------
        # SAVE MASK
        # ----------------------------------------------------

        output_mask = os.path.join(

            MASK_OUTPUT,

            f"{file_stem}.png"
        )

        Image.fromarray(mask).save(
            output_mask
        )

        # ----------------------------------------------------
        # METADATA
        # ----------------------------------------------------

        unique_labels = np.unique(mask)

        semantic_classes = []

        for label in unique_labels:

            if int(label) in LABEL_MAP:

                semantic_classes.append(
                    LABEL_MAP[int(label)]
                )

        metadata = {

            "image": output_img,

            "mask": output_mask,

            "classes": semantic_classes,

            "width": IMG_SIZE,

            "height": IMG_SIZE
        }

        meta_path = os.path.join(

            META_OUTPUT,

            f"{file_stem}.json"
        )

        with open(meta_path, "w") as f:

            json.dump(
                metadata,
                f,
                indent=4
            )

        processed_count += 1

    except Exception as e:

        print(f"\nERROR: {img_path}")
        print(e)

# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n===================================")
print("PREPROCESSING COMPLETE")
print("===================================\n")

print(f"TOTAL PROCESSED : {processed_count}")

print(f"\nOUTPUT PATH:\n{OUTPUT_PATH}")

print("\n===================================\n")