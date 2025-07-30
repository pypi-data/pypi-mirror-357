import functools
import os
import timeit
from pathlib import Path

import matplotlib.pyplot as plt
import orjson


# Function to load JSON using orjson
def load_orjson(fname):
    with open(fname, "rb") as f:
        scene_data = orjson.loads(f.read())
        return scene_data


def check_json(scene_data, view_name):
    return scene_data[view_name]["modality"]


def load_and_check_all(fname, size):
    scene_data = load_orjson(fname)
    for idx in range(size):
        check_json(scene_data, f"{idx:08}")


def fs_check_all(scene_root, size):
    for idx in range(size):
        Path(scene_root, "modality", f"{idx:06}.txt").exists()


def check_individual_jsons(store_root, size):
    for idx in range(size):
        scene_path = Path(store_root, "scene_names", f"{idx:06}")
        scene_meta = load_orjson(Path(scene_path, "meta.json"))
        scene_meta[f"{0:08}"]["modality"]  # TODO: fix this


# Profiling
test_sizes = [2**i for i in range(1, 8)]
STORE_ROOT = "test_data/scene_parsing"
methods = ["check_json", "fs", "indidual_json"]
loading_times = {method: [] for method in methods}
for test_size in test_sizes:
    for method in methods:
        loading_time = -1
        if method == "check_json":
            loading_time = (
                timeit.timeit(
                    functools.partial(
                        load_and_check_all,
                        f"{STORE_ROOT}/size_{test_size:06}.json",
                        test_size,
                    ),
                    number=5,
                )
                * 1000
            )
        elif method == "fs":
            loading_time = (
                timeit.timeit(
                    functools.partial(
                        fs_check_all, Path(STORE_ROOT, f"{test_size:06}"), test_size
                    ),
                    number=5,
                )
                * 1000
            )
        elif method == "indidual_json":
            loading_time = (
                timeit.timeit(
                    functools.partial(check_individual_jsons, STORE_ROOT, test_size),
                    number=5,
                )
                * 1000
            )
        loading_times[method].append(loading_time)

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
plt.title("Loading time by Method and View Size")
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
os.makedirs("plots", exist_ok=True)
plt.savefig("plots/scene_parsing.png", dpi=300)
