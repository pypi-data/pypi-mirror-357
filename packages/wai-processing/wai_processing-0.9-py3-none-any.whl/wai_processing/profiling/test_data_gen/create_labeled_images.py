"""Create some test images for profiling."""

import os
import shutil
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from tqdm import tqdm

from wai import load_data, store_data
from wai.semantics import INVALID_ID, load_semantic_color_mapping

if __name__ == "__main__":
    STORE_ROOT = "test_data/labeled_images"
    if os.path.exists(STORE_ROOT):
        shutil.rmtree(STORE_ROOT)
    os.makedirs(STORE_ROOT)

    semantic_color_mapping = load_semantic_color_mapping()

    # Use a random ASE instance segmentation map for profiling
    fname = "/datasets/AriaSyntheticDataset/20000/render/images/2/instance0000010.png"
    img = np.array(Image.open(fname))
    img = np.rot90(img, axes=(1, 0))

    # Map from pixel values to global instance IDs: global_id = pixel_value - 2
    img = img.astype(np.int32) - 2
    img[img < 0] = INVALID_ID

    # Convert the data to a RGB png, where the color-to-id mapping is stored in the metadata
    out_file = Path(STORE_ROOT) / "res_original.png"
    store_data(
        out_file, img, "labeled_image", semantic_color_mapping=semantic_color_mapping
    )

    # Reload the data and generate multiple resolution and output format variants
    test_resolutions = [(2**i, 2**i) for i in range(7, 14)]
    for w, h in tqdm(test_resolutions):
        image = load_data(out_file, "labeled_image", fmt="np", resize=(w, h))
        # Store as RGB-encoded PNG
        store_data(
            f"{STORE_ROOT}/res_{w:04}x{h:04}.png",
            image,
            "labeled_image",
            semantic_color_mapping=semantic_color_mapping,
        )
        # Store as compressed int32 Numpy array
        store_data(f"{STORE_ROOT}/res_{w:04}x{h:04}.npz", image, "numpy")
        # Store a compressed int32 torch tensor
        store_data(
            f"{STORE_ROOT}/res_{w:04}x{h:04}.ptz", torch.from_numpy(image), "ptz"
        )
