"""Create some test images for profiling."""

import os
import shutil

import numpy as np
from PIL import Image
from tqdm import tqdm


# Function to create a synthetic color image
def create_color_image(width, height):
    "Creates a random img image"
    data = np.random.rand(height, width, 3).astype(np.float32)
    data[data < 0.2] = 0
    return data


if __name__ == "__main__":
    STORE_ROOT = "test_data/color_images"
    if os.path.exists(STORE_ROOT):
        shutil.rmtree(STORE_ROOT)
    os.makedirs(STORE_ROOT)

    # Create and save example color images
    test_resolutions = [(2**i, 2**i) for i in range(7, 14)]
    extensions = ["png", "jpg"]
    for w, h in tqdm(test_resolutions):
        img_data = create_color_image(w, h)
        image = Image.fromarray((img_data * 255).astype(np.uint8))
        for ext in extensions:
            image.save(f"{STORE_ROOT}/res_{w:04}x{h:04}.{ext}")
