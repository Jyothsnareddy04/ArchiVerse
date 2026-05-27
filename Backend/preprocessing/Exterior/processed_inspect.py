# ============================================================
# CMP FACADE PROCESSED DATASET INSPECTOR
# ============================================================
#
# PURPOSE:
# ------------------------------------------------------------
# Validate processed Exterior dataset
#
# CHECKS:
# ------------------------------------------------------------
# 1. Image count
# 2. Mask count
# 3. Metadata count
# 4. Resolution validation
# 5. Semantic class validation
# 6. Unique labels in masks
# 7. Sample visualization
#
# FILE:
# inspect_processed_exterior.py
#
# ============================================================

import os
import cv2
import json
import glob
import numpy as np
import matplotlib.pyplot as plt

from PIL import Image

# ============================================================
# DATASET PATH
# ============================================================

DATASET_PATH = r"C:\Users\jyoth\Desktop\Major-Project\Backend\datasets\processed\Exterior"

IMAGE_PATH = os.path.join(
    DATASET_PATH,
    "images"
)

MASK_PATH = os.path.join(
    DATASET_PATH,
    "masks"
)

META_PATH = os.path.join(
    DATASET_PATH,
    "metadata"
)

# ============================================================
# FIND FILES
# ============================================================

image_files = sorted(
    glob.glob(
        os.path.join(IMAGE_PATH, "*.png")
    )
)

mask_files = sorted(
    glob.glob(
        os.path.join(MASK_PATH, "*.png")
    )
)

meta_files = sorted(
    glob.glob(
        os.path.join(META_PATH, "*.json")
    )
)

# ============================================================
# SUMMARY
# ============================================================

print("\n===================================")
print("PROCESSED EXTERIOR DATASET")
print("===================================\n")

print(f"TOTAL IMAGES    : {len(image_files)}")
print(f"TOTAL MASKS     : {len(mask_files)}")
print(f"TOTAL METADATA  : {len(meta_files)}")

# ============================================================
# VALIDATION COUNTERS
# ============================================================

invalid_images = 0
invalid_masks = 0
missing_metadata = 0

all_classes = set()

# ============================================================
# VALIDATE FILES
# ============================================================

for idx in range(len(image_files)):

    try:

        image_path = image_files[idx]

        file_stem = os.path.splitext(
            os.path.basename(image_path)
        )[0]

        mask_path = os.path.join(
            MASK_PATH,
            f"{file_stem}.png"
        )

        meta_path = os.path.join(
            META_PATH,
            f"{file_stem}.json"
        )

        # ----------------------------------------------------
        # IMAGE
        # ----------------------------------------------------

        image = cv2.imread(image_path)

        if image is None:

            invalid_images += 1
            continue

        # ----------------------------------------------------
        # MASK
        # ----------------------------------------------------

        mask = np.array(
            Image.open(mask_path)
        )

        if mask is None:

            invalid_masks += 1
            continue

        # ----------------------------------------------------
        # METADATA
        # ----------------------------------------------------

        if not os.path.exists(meta_path):

            missing_metadata += 1
            continue

        with open(meta_path, "r") as f:

            metadata = json.load(f)

        for cls in metadata["classes"]:

            all_classes.add(cls)

    except Exception as e:

        print(f"\nERROR: {image_path}")
        print(e)

# ============================================================
# SUMMARY
# ============================================================

print("\n===================================")
print("VALIDATION SUMMARY")
print("===================================\n")

print(f"INVALID IMAGES    : {invalid_images}")
print(f"INVALID MASKS     : {invalid_masks}")
print(f"MISSING METADATA  : {missing_metadata}")

# ============================================================
# SEMANTIC CLASSES
# ============================================================

print("\n===================================")
print("SEMANTIC CLASSES FOUND")
print("===================================\n")

for cls in sorted(all_classes):

    print(cls)

# ============================================================
# SAMPLE VISUALIZATION
# ============================================================

sample_idx = 0

sample_image_path = image_files[sample_idx]

sample_stem = os.path.splitext(
    os.path.basename(sample_image_path)
)[0]

sample_mask_path = os.path.join(
    MASK_PATH,
    f"{sample_stem}.png"
)

sample_meta_path = os.path.join(
    META_PATH,
    f"{sample_stem}.json"
)

# ------------------------------------------------------------
# LOAD SAMPLE
# ------------------------------------------------------------

image = cv2.imread(sample_image_path)

image = cv2.cvtColor(
    image,
    cv2.COLOR_BGR2RGB
)

mask = np.array(
    Image.open(sample_mask_path)
)

with open(sample_meta_path, "r") as f:

    metadata = json.load(f)

# ============================================================
# SAMPLE INFO
# ============================================================

print("\n===================================")
print("SAMPLE DATA")
print("===================================\n")

print(f"IMAGE : {sample_image_path}")

print(f"\nIMAGE SHAPE : {image.shape}")

print(f"\nMASK SHAPE : {mask.shape}")

print(f"\nCLASSES :")

for cls in metadata["classes"]:

    print(f" - {cls}")

print(f"\nUNIQUE MASK VALUES:")

print(np.unique(mask))

# ============================================================
# VISUALIZATION
# ============================================================

plt.figure(figsize=(12,6))

# ------------------------------------------------------------
# IMAGE
# ------------------------------------------------------------

plt.subplot(1,2,1)

plt.imshow(image)

plt.title("Facade Image")

plt.axis("off")

# ------------------------------------------------------------
# MASK
# ------------------------------------------------------------

plt.subplot(1,2,2)

plt.imshow(mask)

plt.title("Semantic Mask")

plt.axis("off")

plt.show()

# ============================================================
# FINAL STATUS
# ============================================================

print("\n===================================")

if (

    invalid_images == 0 and
    invalid_masks == 0 and
    missing_metadata == 0

):

    print("DATASET LOOKS VALID")

else:

    print("DATASET HAS ISSUES")

print("===================================\n")