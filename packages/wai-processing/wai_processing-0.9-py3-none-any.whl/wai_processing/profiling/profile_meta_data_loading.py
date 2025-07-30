import functools
import json
import os
import timeit

import matplotlib.pyplot as plt
import orjson
import oyaml
import yaml
from ruamel.yaml import YAML

ruaml = YAML(typ="rt")


# Function to load JSON using orjson
def load_orjson(fname):
    with open(fname, "rb") as f:
        return orjson.loads(f.read())


def load_json(fname):
    with open(fname, "rb") as f:
        return json.load(f)


# Function to load YAML using PyYAML with CLoader
def load_yaml(fname):
    try:
        from yaml import CLoader as Loader
    except ImportError:
        from yaml import Loader
    with open(fname, "r", encoding="utf-8") as f:
        return yaml.load(f, Loader=Loader)


def load_oyaml(fname):
    try:
        from oyaml import CLoader as Loader
    except ImportError:
        from oyaml import Loader
    with open(fname, "r", encoding="utf-8") as f:
        return oyaml.load(f, Loader=Loader)


def load_ruamel(fname):
    with open(fname, "r", encoding="utf-8") as f:
        return ruaml.load(f)


# Profiling
test_sizes = [2**i for i in range(6, 18)]
store_root = "test_data/meta_data"
methods = ["json", "orjson"]  # ,  "yaml"]#, "ruamel"]
loading_times = {method: [] for method in methods}
for test_size in test_sizes:
    fn = f"{store_root}/size_{test_size:06}"
    for method in methods:
        loading_time = 0
        if method == "json":
            loading_time = timeit.timeit(
                functools.partial(load_json, f"{fn}.json"), number=5
            )
        elif method == "orjson":
            loading_time = timeit.timeit(
                functools.partial(load_orjson, f"{fn}.json"), number=5
            )
        elif method == "yaml":
            loading_time = timeit.timeit(
                functools.partial(load_yaml, f"{fn}.yaml"), number=5
            )
        elif method == "ruamel":
            loading_time = timeit.timeit(
                functools.partial(load_ruamel, f"{fn}.yaml"), number=5
            )
        loading_times[method].append(1000 * loading_time)
# Plot file sizes
plt.figure(figsize=(10, 6))

for method in methods:
    plt.plot(
        [str(test_size) for test_size in test_sizes],
        loading_times[method],
        label=method,
    )
plt.xlabel("Meta entry size")
plt.ylabel("Loading time (ms)")
plt.title("Loading time by Method and Meta Size")
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
os.makedirs("plots", exist_ok=True)
plt.savefig("plots/meta_loading.png", dpi=300)
