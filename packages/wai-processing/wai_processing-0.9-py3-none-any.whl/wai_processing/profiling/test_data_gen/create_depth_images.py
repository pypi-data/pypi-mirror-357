"""Create some test camera data for profiling."""

import gzip
import os
import pickle
import shutil

import cv2
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, PngImagePlugin
from tqdm import tqdm

os.environ["OPENCV_IO_ENABLE_OPENEXR"] = "1"


def create_random_depth_map(width, height, max_depth=10):
    """Creates a random depth map with depth in [0, 9.5] meters, and some invalid pixels."""
    depth_data = np.random.rand(height, width).astype(np.float32) * max_depth - 0.5
    depth_data[depth_data < 0] = -1
    depth_data[(depth_data > 0.0) & (depth_data < 0.1)] = 0.1  # some constant values
    return depth_data


def create_synthetic_depth_map(width, height):
    """Creates a synthetic test depth map with a sphere on a slanted plane, with invalid padding"""
    x, y = np.meshgrid(
        np.arange(width, dtype=np.float32), np.arange(height, dtype=np.float32)
    )

    ## slanted plane
    a = 0.9 / (width - 1)
    b = -9 / (height - 1)
    c = 9.1
    depth = a * x + b * y + c

    ## sphere under orthographic projection
    sphere_radius = (width + height) / 10  # in pixels
    radius_pixels = np.sqrt((x - width / 2) ** 2 + (y - height / 2) ** 2)
    radius = np.clip(
        radius_pixels / sphere_radius, 0, 1
    )  # normalised to 0/center, 1/boundary
    sphere_mask = radius_pixels < sphere_radius
    depth[sphere_mask] = 1.5 - 1 * np.sqrt(1 - radius[sphere_mask] ** 2)

    ## add some noise
    depth += 0.05 * np.random.randn(height, width).astype(np.float32)

    ## add invalid padding left and right
    padding = max(20, (width - height) // 2)
    depth[:, :padding] = -1
    depth[:, width - padding :] = -1

    return depth


def save_depth_as_png(fname, depth_data):
    image = Image.fromarray((1000 * depth_data).astype(np.uint16))
    metadata = PngImagePlugin.PngInfo()
    metadata.add_text("scale", "1000")
    image.save(fname, pnginfo=metadata)


def save_depth_as_tiff(fname, depth_data):
    image = Image.fromarray(depth_data.astype(np.float32))
    image.save(fname)


def save_depth_as_exr(fname, depth_data):
    cv2.imwrite(fname, depth_data)


def save_depth_as_npz(fname, depth_data):
    np.savez_compressed(fname, depth_data=depth_data)


def save_depth_as_pickle(fname, depth_data):
    # Save the array with gzip compression
    with gzip.open(fname, "wb") as f:
        pickle.dump(depth_data, f)


if __name__ == "__main__":
    # create depth images and plot image sizes
    test_resolutions = [(2**i, 2**i) for i in range(7, 14)]
    STORE_ROOT = "test_data/depth_images"
    if os.path.exists(STORE_ROOT):
        shutil.rmtree(STORE_ROOT)
    os.makedirs(STORE_ROOT)

    # Create and save example depth images
    for w, h in tqdm(test_resolutions, "Creating test depth maps"):
        # depth_map = create_random_depth_map(w, h)
        depth_map = create_synthetic_depth_map(w, h)
        fn = f"{STORE_ROOT}/res_{w:04}x{h:04}"
        save_depth_as_png(f"{fn}.png", depth_map)
        save_depth_as_tiff(f"{fn}.tiff", depth_map)
        save_depth_as_exr(f"{fn}.exr", depth_map)
        save_depth_as_npz(f"{fn}.npz", depth_map)
        save_depth_as_npz(f"{fn}.npz16", (1000 * depth_map).astype(np.uint16))
        save_depth_as_pickle(f"{fn}.pkl.gz", depth_map)
        # add comments

    extensions = ["png", "tiff", "exr", "npz", "npz16.npz", "pkl.gz"]
    file_sizes = {ext: [] for ext in extensions}
    for w, h in test_resolutions:
        for ext in extensions:
            fn = f"{STORE_ROOT}/res_{w:04}x{h:04}.{ext}"
            file_sizes[ext].append(os.path.getsize(fn))

    # Plot file sizes
    plt.figure(figsize=(10, 6))
    for ext in extensions:
        plt.semilogy(
            [f"{w}x{h}" for w, h in test_resolutions],
            file_sizes[ext],
            label=ext,
        )
    plt.xlabel("Resolution")
    plt.ylabel("File Size (Bytes)")
    plt.title("Depth Map File Size by Format and Resolution")
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    os.makedirs("plots", exist_ok=True)
    plt.savefig("plots/depth_sizes.png", dpi=300)
