"""Create some scene parsing test data for profiling."""

import json
import os
import shutil
from pathlib import Path


# Generate a large dataset
def create_scene_json(num_entries=10000):
    scene_meta = {f"{i:08}": {"modality": True} for i in range(num_entries)}
    return scene_meta


def create_individual_scene_jsons(store_root, num_entries):
    for idx in range(num_entries):
        scene_path = Path(store_root, "scene_names", f"{idx:06}")
        os.makedirs(scene_path)
        scene_meta = {f"{i:08}": {"modality": True} for i in range(5)}
        create_json_file(Path(scene_path, "meta.json"), scene_meta)


# Create JSON file
def create_json_file(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f)


def create_parsing_files(store_root, num_entries):
    modality_path = Path(store_root, f"{num_entries:06}", "modality")
    os.makedirs(modality_path)
    for entry_idx in range(num_entries):
        # create a dummy scene
        with open(modality_path / f"{entry_idx:06}.txt", "w", encoding="utf-8") as f:
            f.write(str(entry_idx))


if __name__ == "__main__":
    STORE_ROOT = "test_data/scene_parsing"
    if os.path.exists(STORE_ROOT):
        shutil.rmtree(STORE_ROOT)
    os.makedirs(STORE_ROOT)

    # Create and save example depth images
    test_sizes = [2**i for i in range(1, 12)]
    for test_size in test_sizes:
        scene_json = create_scene_json(test_size)
        fn = f"{STORE_ROOT}/size_{test_size:06}"
        create_json_file(f"{fn}.json", scene_json)
        create_parsing_files(STORE_ROOT, test_size)
    create_individual_scene_jsons(STORE_ROOT, max(test_sizes))
