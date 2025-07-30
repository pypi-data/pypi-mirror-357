import functools
import os
import timeit

import bson
import matplotlib.pyplot as plt
import numpy as np
import orjson


# Function to load JSON using orjson
def load_orjson(fname):
    with open(fname, "rb") as f:
        camera_data = orjson.loads(f.read())
        return camera_data


def load_orjson_arr(fname):
    camera_data = load_orjson(fname)
    camera_data["extrinsics"] = np.array(camera_data["extrinsics"])
    camera_data["intrinsics"] = np.array(camera_data["intrinsics"])
    return camera_data


def load_nerfstudio(fname):
    camera_data = load_orjson(fname)
    camera_data["extrinsics"] = np.array(
        [fname["transform_matrix"] for fname in camera_data["frames"]]
    )
    return camera_data


def load_bson(fname):
    with open(fname, "rb") as f:
        camera_data = bson.loads(f.read())
        camera_data["extrinsics"] = np.array(camera_data["extrinsics"])
        camera_data["intrinsics"] = np.array(camera_data["intrinsics"])
        return camera_data


def load_numpy_cam_data(filename):
    extrinsics = np.load(f"{filename}_extrinsics.npy")
    intrinsics = np.load(f"{filename}_intrinsics.npy")
    with open(f"{filename}_meta.json", "rb") as f:
        cam_data = orjson.loads(f.read())
    return extrinsics, intrinsics, cam_data


# Profiling
test_sizes = [2**i for i in range(6, 14)]
store_root = "test_data/camera_data"
methods = ["orjson", "numpy", "nerfstudio"]  # "bson" ]
loading_times = {method: [] for method in methods}
for test_size in test_sizes:
    fn = f"{store_root}/size_{test_size:06}"
    for method in methods:
        loading_time = 0
        if method == "orjson":
            loading_time = timeit.timeit(
                functools.partial(load_orjson_arr, f"{fn}.json"), number=5
            )
        elif method == "numpy":
            loading_time = timeit.timeit(
                functools.partial(load_numpy_cam_data, fn), number=5
            )
        elif method == "bson":
            loading_time = timeit.timeit(
                functools.partial(load_bson, f"{fn}.bson"), number=5
            )
        elif method == "nerfstudio":
            loading_time = timeit.timeit(
                functools.partial(load_nerfstudio, f"{fn}_transforms.json"), number=5
            )
        loading_times[method].append(1000 * loading_time)  # ms

# Plot file sizes
plt.figure(figsize=(10, 6))

for method in methods:
    plt.plot(
        [str(test_size) for test_size in test_sizes],
        loading_times[method],
        label=method,
    )
plt.xlabel("View size")
plt.ylabel("Loading time (ms)")
plt.title("Loading time by Method and Camera Loading")
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
os.makedirs("plots", exist_ok=True)
plt.savefig("plots/camera_loading.png", dpi=300)
