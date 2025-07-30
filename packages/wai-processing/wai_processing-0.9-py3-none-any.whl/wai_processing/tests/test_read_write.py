import hashlib
import json
import logging
import os
import sys

import numpy as np
from tqdm import tqdm

sys.path.append(".")
sys.path.append("..")
from wai import load_data, store_data
from wai.profiling.test_data_gen.create_color_images import create_color_image
from wai.profiling.test_data_gen.create_depth_images import create_random_depth_map
from wai.profiling.test_data_gen.create_meta_data import create_meta_data

## Set up basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

def recursive_hash(obj):
    if isinstance(obj, dict):
        # Convert the dict to a JSON string and sort the keys
        json_string = json.dumps(obj, sort_keys=True)

        # Calculate the hash of the JSON string
        return hashlib.sha256(json_string.encode()).hexdigest()

    elif isinstance(obj, list):
        # Recursively calculate the hashes of each element in the list
        hashes = [recursive_hash(x) for x in obj]

        # Sort the hashes and join them into a single string
        combined_string = "".join(sorted(hashes))

        # Calculate the hash of the combined string
        return hashlib.sha256(combined_string.encode()).hexdigest()

    else:
        # If the object is not a dict or list, raise an error
        raise ValueError("Unsupported type: {}".format(type(obj)))


STORE_ROOT = "test_data/wai_test"
DEPTH_SCALE = 1000

os.makedirs(STORE_ROOT, exist_ok=True)

test_sizes = [2**i for i in range(7, 10)]
for test_size in tqdm(test_sizes):
    color_img = create_color_image(test_size, test_size)
    depth_data = create_random_depth_map(test_size, test_size)
    meta_data = create_meta_data(test_size)
    arr_data = np.random.rand(test_size, 5)

    color_fn = f"{STORE_ROOT}/color_{test_size:04}.png"
    depth_fn = f"{STORE_ROOT}/depth_{test_size:04}.png"
    range_fn = f"{STORE_ROOT}/range_{test_size:04}.exr"
    meta_fn = f"{STORE_ROOT}/meta_{test_size:04}.json"
    arr_fn = f"{STORE_ROOT}/arr_{test_size:04}.npz"

    store_data(color_fn, color_img)
    store_data(depth_fn, depth_data, "depth", depth_scale=DEPTH_SCALE)
    store_data(range_fn, depth_data)
    store_data(meta_fn, meta_data)
    store_data(arr_fn, arr_data)

    loaded_color_img = load_data(color_fn)
    assert np.allclose(loaded_color_img.permute(1, 2, 0), color_img, atol=1e-2)

    loaded_depth_data = load_data(depth_fn, "depth")
    assert np.allclose(loaded_depth_data, depth_data, atol=1 / DEPTH_SCALE)

    loaded_range_data = load_data(range_fn)
    assert np.allclose(loaded_range_data, depth_data, atol=1e-5)

    loaded_meta_data = load_data(meta_fn)
    assert recursive_hash(meta_data) == recursive_hash(loaded_meta_data)

    loaded_arr_data = load_data(arr_fn)
    assert np.allclose(arr_data, loaded_arr_data)

logger.info("All tests passed")
