import functools
import os
import timeit

import matplotlib.pyplot as plt
import numpy as np
import torch
from PIL import Image
from tqdm import tqdm

from wai import load_data


def load_png_without_remap(fname, fmt="torch", resize=None):
    with open(fname, "rb") as f:
        pil_image = Image.open(f)
        pil_image.load()
        if pil_image.mode != "RGB":
            raise OSError(
                f"Expected a RGB image in {fname}, but instead found an image with mode {pil_image.mode}"
            )

        if resize is not None:
            pil_image = pil_image.resize(resize, Image.NEAREST)

    if fmt == "pil":
        return pil_image
    elif fmt == "np":
        return np.array(pil_image)
    elif fmt == "torch":
        return torch.from_numpy(np.array(pil_image))
    else:
        raise NotImplementedError(f"Image format not supported: {fmt}")


if __name__ == "__main__":
    # Profiling
    test_resolutions = [(2**i, 2**i) for i in range(7, 14)]
    DATA_ROOT = "test_data/labeled_images"
    STORE_ROOT = "wai/profiling/plots"
    methods = [
        "PNG with remap",
        "PNG without remap",
        "npz (int32)",
        "ptz (int32)",
    ]
    loading_times = {f"{method}": [] for method in methods}
    file_sizes = {f"{method}": [] for method in methods}
    for test_res in tqdm(test_resolutions, "Loading images"):
        for method in methods:
            if method == "PNG with remap":
                fn = f"{DATA_ROOT}/res_{test_res[0]:04}x{test_res[1]:04}.png"
                loading_time = timeit.timeit(
                    functools.partial(
                        load_data,
                        fn,
                        "labeled_image",
                        fmt="np",
                    ),
                    number=5,
                )
            elif method == "PNG without remap":
                fn = f"{DATA_ROOT}/res_{test_res[0]:04}x{test_res[1]:04}.png"
                loading_time = timeit.timeit(
                    functools.partial(
                        load_png_without_remap,
                        fn,
                        fmt="np",
                    ),
                    number=5,
                )
            elif method == "npz (int32)":
                fn = f"{DATA_ROOT}/res_{test_res[0]:04}x{test_res[1]:04}.npz"
                loading_time = timeit.timeit(
                    functools.partial(load_data, fn),
                    number=5,
                )
            elif method == "ptz (int32)":
                fn = f"{DATA_ROOT}/res_{test_res[0]:04}x{test_res[1]:04}.ptz"
                loading_time = timeit.timeit(
                    functools.partial(load_data, fn),
                    number=5,
                )
            else:
                raise NotImplementedError
            loading_times[f"{method}"].append(1000 * loading_time)  # ms
            file_sizes[f"{method}"].append(os.path.getsize(fn) / (1024 * 1024))

    # Plot loading speed
    plt.figure(figsize=(10, 6))
    for method in methods:
        plt.plot(
            [f"{res[0]}x{res[1]}" for res in test_resolutions],
            loading_times[f"{method}"],
            label=f"{method}",
        )
    plt.xlabel("Image resolution")
    plt.ylabel("Loading time [ms]")
    plt.title("Loading time by method and resolution")
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    os.makedirs(STORE_ROOT, exist_ok=True)
    plt.savefig(f"{STORE_ROOT}/labeled_image_loading.png", dpi=300)

    # Plot file size
    plt.figure(figsize=(10, 6))
    for method in methods:
        plt.plot(
            [f"{res[0]}x{res[1]}" for res in test_resolutions],
            file_sizes[f"{method}"],
            label=f"{method}",
        )
    plt.xlabel("Image resolution")
    plt.ylabel("File size [MB]")
    plt.title("File size by method and resolution")
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{STORE_ROOT}/labeled_image_filesize.png", dpi=300)
