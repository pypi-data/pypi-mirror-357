import functools
import os
import timeit
from pathlib import Path

import matplotlib.pyplot as plt
from box import Box

from wai import load_data
from wai.utils import get_scene_frame_names


def exr_load_batch(
    scene_dir, frame_names, modality_path="metric3dv2/v0/depth_debug", batch_size=10
):
    for frame_name in frame_names[:batch_size]:
        _ = load_data(Path(scene_dir, modality_path, f"{frame_name}.exr"))


def png_load_batch(
    scene_dir, frame_names, modality_path="metric3dv2/v0/depth", batch_size=10
):
    for frame_name in frame_names[:batch_size]:
        _ = load_data(Path(scene_dir, modality_path, f"{frame_name}.png"), "depth")


cfg = Box(root="/fsx/normanm/dl3dv_10k_wai", scene_filters=[{"exists": "metric3dv2"}])
scene_frames = get_scene_frame_names(cfg)


batch_sizes = [1, 2, 4, 6, 8, 10]
methods = ["png", "exr"]
loading_times = {method: [] for method in methods}
for scene_name, frame_names in scene_frames.items():
    scene_root = Path(cfg.root) / scene_name
    # some warmup
    exr_load_batch(
        scene_root, frame_names, modality_path="metric3dv2/v0/depth_debug", batch_size=1
    )
    png_load_batch(
        scene_root, frame_names, modality_path="metric3dv2/v0/depth", batch_size=1
    )
    unseen_frame_names = frame_names[1:]
    for batch_size in batch_sizes:
        for method in methods:
            if method == "exr":
                loading_time = timeit.timeit(
                    functools.partial(
                        exr_load_batch,
                        scene_root,
                        unseen_frame_names,
                        modality_path="metric3dv2/v0/depth_debug",
                        batch_size=batch_size,
                    ),
                    number=1,
                )
            elif method == "png":
                loading_time = timeit.timeit(
                    functools.partial(
                        png_load_batch,
                        scene_root,
                        unseen_frame_names,
                        modality_path="metric3dv2/v0/depth",
                        batch_size=batch_size,
                    ),
                    number=1,
                )
            else:
                raise NotImplementedError
            unseen_frame_names = unseen_frame_names[batch_size:]
            loading_times[method].append(1000 * loading_time)  # ms
    break  # one scene only

# Plot loading times
plt.figure(figsize=(10, 6))
for method in methods:
    plt.plot(
        [str(batch_size) for batch_size in batch_sizes],
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
plt.savefig("profiling/plots/depth_loading.png", dpi=300)
