"""Profile EXR image file size, writing and loading."""

import functools
import gzip
import io
import os
import shutil
import sys
import timeit

import cv2
import numpy as np
import torch

sys.path.append(".")
sys.path.append("..")
from profiling.test_data_gen.create_depth_images import (
    # create_random_depth_map,
    create_synthetic_depth_map,
)

from wai import load_data, store_data
from wai.io import _load_ptz, _store_ptz

os.environ["OPENCV_IO_ENABLE_OPENEXR"] = "1"


def write_exr_opencv(filename, data, params=None) -> bool:
    """Writes a NumPy array as an EXR image using OpenCV."""
    if data.dtype != np.float32:
        ## Note: only 32-bit float (CV_32F) images can be saved
        data = data.astype(np.float32)
    return cv2.imwrite(filename, data, params if params else [])


def read_exr_opencv(filename):
    """Loads as an EXR image as a NumPy array using OpenCV."""
    return cv2.imread(filename, cv2.IMREAD_UNCHANGED)


def read_ptz_unsafe(filename):
    """Reads a PTZ in an unsafe manner, e.g. to unpickle NumPy arrays."""
    with open(filename, "rb") as fid:
        data = gzip.decompress(fid.read())
        return torch.load(io.BytesIO(data), map_location="cpu", weights_only=False)


def benchmark_exr_formats():
    opencv_params = {
        "nocompress": [
            cv2.IMWRITE_EXR_COMPRESSION,
            cv2.IMWRITE_EXR_COMPRESSION_NO,
        ],
        "default": [],  # == float + zip
        # "zip": [  # to check this is the default
        #     cv2.IMWRITE_EXR_TYPE,
        #     cv2.IMWRITE_EXR_TYPE_FLOAT,
        #     cv2.IMWRITE_EXR_COMPRESSION,
        #     cv2.IMWRITE_EXR_COMPRESSION_ZIP,
        # ],
        "rle": [
            cv2.IMWRITE_EXR_COMPRESSION,
            cv2.IMWRITE_EXR_COMPRESSION_RLE,
        ],
        "piz": [
            cv2.IMWRITE_EXR_COMPRESSION,
            cv2.IMWRITE_EXR_COMPRESSION_PIZ,
        ],
        "pxr24": [
            cv2.IMWRITE_EXR_COMPRESSION,
            cv2.IMWRITE_EXR_COMPRESSION_PXR24,
        ],
        "b44": [
            cv2.IMWRITE_EXR_COMPRESSION,
            cv2.IMWRITE_EXR_COMPRESSION_ZIPS,
        ],
        # "dwaa": [  # abs error = 1.4e-01, rel error = 8.3e-02 is too high
        #     cv2.IMWRITE_EXR_COMPRESSION,
        #     cv2.IMWRITE_EXR_COMPRESSION_DWAA,
        # ],
        # "dwab": [  # abs error = 1.4e-01, rel error = 8.3e-02 is too high
        #     cv2.IMWRITE_EXR_COMPRESSION,
        #     cv2.IMWRITE_EXR_COMPRESSION_DWAB,
        # ],
        "zips": [
            cv2.IMWRITE_EXR_COMPRESSION,
            cv2.IMWRITE_EXR_COMPRESSION_ZIPS,
        ],
        ## half modes below
        "half-nocompress": [
            cv2.IMWRITE_EXR_TYPE,
            cv2.IMWRITE_EXR_TYPE_HALF,
            cv2.IMWRITE_EXR_COMPRESSION,
            cv2.IMWRITE_EXR_COMPRESSION_NO,
        ],
        "half-rle": [
            cv2.IMWRITE_EXR_TYPE,
            cv2.IMWRITE_EXR_TYPE_HALF,
            cv2.IMWRITE_EXR_COMPRESSION,
            cv2.IMWRITE_EXR_COMPRESSION_RLE,
        ],
        # "half-b44": [  # 2.5e-01, rel error = 5.1e-02 is too high
        #     cv2.IMWRITE_EXR_TYPE,
        #     cv2.IMWRITE_EXR_TYPE_HALF,
        #     cv2.IMWRITE_EXR_COMPRESSION,
        #     cv2.IMWRITE_EXR_COMPRESSION_B44,
        # ],
        # "half-dwaa": [  # abs error = 1.4e-01, rel error = 8.3e-02 is too high
        #     cv2.IMWRITE_EXR_TYPE,
        #     cv2.IMWRITE_EXR_TYPE_HALF,
        #     cv2.IMWRITE_EXR_COMPRESSION,
        #     cv2.IMWRITE_EXR_COMPRESSION_DWAA,
        # ],
        # "half-dwab": [  # abs error = 1.4e-01, rel error = 8.3e-02 is too high
        #     cv2.IMWRITE_EXR_TYPE,
        #     cv2.IMWRITE_EXR_TYPE_HALF,
        #     cv2.IMWRITE_EXR_COMPRESSION,
        #     cv2.IMWRITE_EXR_COMPRESSION_DWAB,
        # ],
        "half-piz": [
            cv2.IMWRITE_EXR_TYPE,
            cv2.IMWRITE_EXR_TYPE_HALF,
            cv2.IMWRITE_EXR_COMPRESSION,
            cv2.IMWRITE_EXR_COMPRESSION_PIZ,
        ],
        "half-pxr24": [
            cv2.IMWRITE_EXR_TYPE,
            cv2.IMWRITE_EXR_TYPE_HALF,
            cv2.IMWRITE_EXR_COMPRESSION,
            cv2.IMWRITE_EXR_COMPRESSION_PXR24,
        ],
        "half-zip": [
            cv2.IMWRITE_EXR_TYPE,
            cv2.IMWRITE_EXR_TYPE_HALF,
            cv2.IMWRITE_EXR_COMPRESSION,
            cv2.IMWRITE_EXR_COMPRESSION_ZIP,
        ],
        "half-zips": [
            cv2.IMWRITE_EXR_TYPE,
            cv2.IMWRITE_EXR_TYPE_HALF,
            cv2.IMWRITE_EXR_COMPRESSION,
            cv2.IMWRITE_EXR_COMPRESSION_ZIPS,
        ],
    }

    methods = [
        {
            "name": "wai PNG",
            "filename": "{STORE_ROOT}/opencv_wai_png_{test_size:04}.png",
            "write": functools.partial(store_data, format="depth", depth_scale=1000),
            "read": lambda x: load_data(x, format="depth").numpy(),
        },
        {
            "name": "PTZ-NumPy",
            "filename": "{STORE_ROOT}/opencv_ptz_numpy_{test_size:04}.png",
            "write": _store_ptz,
            "read": read_ptz_unsafe,
        },
        {
            "name": "PTZ-NumPy-float16",
            "filename": "{STORE_ROOT}/opencv_ptz_numpy_float16_{test_size:04}.png",
            "write": lambda fn, x: _store_ptz(fn, x.astype(np.float16)),
            "read": read_ptz_unsafe,
        },
        {
            "name": "PTZ-PyTorch",
            "filename": "{STORE_ROOT}/opencv_ptz_pytorch_{test_size:04}.png",
            "write": lambda fn, x: _store_ptz(fn, torch.from_numpy(x)),
            "read": lambda x: _load_ptz(x).numpy(),
        },
        {
            "name": "PTZ-PyTorch-float16",
            "filename": "{STORE_ROOT}/opencv_ptz_pytorch_float16_{test_size:04}.png",
            "write": lambda fn, x: _store_ptz(
                fn, torch.from_numpy(x.astype(np.float16))
            ),
            "read": lambda x: _load_ptz(x).numpy(),
        },
    ]
    for label, opencv_param in opencv_params.items():
        methods.append(
            {
                "name": f"OpenCV {label}",
                "filename": f"{{STORE_ROOT}}/opencv_{label}_{{test_size:04}}.exr",
                "write": functools.partial(write_exr_opencv, params=opencv_param),
                "read": read_exr_opencv,
            }
        )

    STORE_ROOT = "test_data/exr_images"
    if os.path.exists(STORE_ROOT):
        shutil.rmtree(STORE_ROOT)
    os.makedirs(STORE_ROOT, exist_ok=True)

    test_sizes = [2**i for i in range(7, 12)]
    for test_size in test_sizes:
        ## Generate test depth map
        # depth = create_random_depth_map(test_size, test_size)
        depth = create_synthetic_depth_map(test_size, test_size)
        # depth = depth.astype(np.float16)  # make input depth 16-bit

        ## Profile image writing, measuring time and file size
        for method in methods:
            filename = method["filename"].format(**locals())
            save_time = timeit.timeit(
                functools.partial(method["write"], filename, depth),
                number=10,
            )
            save_time /= 10  # average runtime over the 10 benchmarking runs
            file_size = os.path.getsize(filename)
            print(
                f"Saving  {test_size}x{test_size} with {method['name']:22}: "
                f"{1000 * save_time:5.1f} ms, {file_size:10,} B"
            )

        print()

        ## Profile image reading, measuring time and bandwidth
        for method in methods:
            filename = method["filename"].format(**locals())

            load_time = timeit.timeit(
                functools.partial(method["read"], filename),
                number=10,
            )
            load_time /= 10  # average runtime over the 10 benchmarking runs
            file_size = os.path.getsize(filename)
            print(
                f"Loading {test_size}x{test_size} with {method['name']:22}: "
                f"{1000 * load_time:5.1f} ms, {file_size:10,} B, "
                f"{file_size / load_time / 1024**2:6.1f} MB/s"
            )

        print()

        ## Validate correctness by computing absolute/relative errors
        for method in methods:
            filename = method["filename"].format(**locals())

            read_depth = method["read"](filename)
            # print(type(read_depth))
            abs_err = np.max(np.abs(depth - read_depth))
            rel_err = np.max(np.abs(1 - depth / read_depth))
            print(
                f"Testing {test_size}x{test_size} with {method['name']:22}: "
                f"abs error = {abs_err:.1e}, rel error = {rel_err:.1e}"
            )

        print()


if __name__ == "__main__":

    benchmark_exr_formats()
