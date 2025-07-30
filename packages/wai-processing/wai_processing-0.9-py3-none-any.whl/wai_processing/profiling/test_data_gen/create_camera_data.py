"""Create some test camera data for profiling."""

import json
import os
import shutil

import bson
import numpy as np
from tqdm import tqdm


def create_camera_params(size):
    return np.random.rand(size, 4, 4), np.random.rand(size, 3, 3)


# Create JSON file
def create_json_file(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f)


def create_bson_file(filename, data):
    with open(filename, "wb") as f:
        f.write(bson.dumps(data))


def create_nerfstudio_transform(size):
    random_extrinsics = np.random.rand(size, 4, 4)
    frames = [
        {
            "transform_matrix": random_extrinsics[idx].tolist(),
            "camera_model": "OPENCV_FISHEYE",
            "fl_x": 1072.0,
            "fl_y": 1068.0,
            "cx": 1504.0,
            "cy": 1000.0,
        }
        for idx in range(size)
    ]
    transforms = {"frames": frames}
    return transforms


if __name__ == "__main__":
    test_sizes = [2**i for i in range(6, 18)]
    STORE_ROOT = "test_data/camera_data"
    if os.path.exists(STORE_ROOT):
        shutil.rmtree(STORE_ROOT)
    os.makedirs(STORE_ROOT)

    # Create and save example camera data
    for test_size in tqdm(test_sizes):
        extrinsics, intrinsics = create_camera_params(test_size)
        fn = f"{STORE_ROOT}/size_{test_size:06}"
        create_json_file(
            f"{fn}.json",
            {"intrinsics": intrinsics.tolist(), "extrinsics": extrinsics.tolist()},
        )
        create_json_file(
            f"{fn}_transforms.json", create_nerfstudio_transform(test_size)
        )
        create_bson_file(
            f"{fn}.bson",
            {"intrinsics": intrinsics.tolist(), "extrinsics": extrinsics.tolist()},
        )
        np.save(f"{fn}_extrinsics.npy", extrinsics)
        np.save(f"{fn}_intrinsics.npy", intrinsics)
        create_json_file(
            f"{fn}_meta.json",
            {"view_names": {str(idx): idx for idx in range(len(extrinsics))}},
        )
