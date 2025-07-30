"""Create some test meta data for profiling."""

import json
import os
import random
import shutil

import matplotlib.pyplot as plt
import yaml
from tqdm import tqdm


# Generate a large dataset
def create_meta_data(num_entries=10000):
    return [
        {
            "index": i,
            "image_name": f"image_{i:05}.jpg",
            "metadata": {
                "resolution": f"{random.randint(800, 4000)}x{random.randint(600, 3000)}",
                "format": random.choice(["JPEG", "PNG", "BMP"]),
                "date_processed": f"2023-{random.randint(1, 12):02}-{random.randint(1, 28):02}",
            },
        }
        for i in range(num_entries)
    ]


# Create JSON file
def create_json_file(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f)


# Create YAML file
def create_yaml_file(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False)


if __name__ == "__main__":
    STORE_ROOT = "test_data/meta_data"
    if os.path.exists(STORE_ROOT):
        shutil.rmtree(STORE_ROOT)
    os.makedirs(STORE_ROOT)

    # Create and save example meta data images
    test_sizes = [2**i for i in range(6, 18)]
    for test_size in tqdm(test_sizes, "Creating test meta data"):
        meta_data = create_meta_data(test_size)
        fn = f"{STORE_ROOT}/size_{test_size:06}"
        create_json_file(f"{fn}.json", meta_data)
        create_yaml_file(f"{fn}.yaml", meta_data)

    extensions = ["json", "yaml"]
    file_sizes = {ext: [] for ext in extensions}
    for test_size in test_sizes:
        for ext in extensions:
            fn = f"{STORE_ROOT}/size_{test_size:06}.{ext}"
            file_sizes[ext].append(os.path.getsize(fn) / 1024)  # Convert to kilobytes

    # Plot file sizes
    plt.figure(figsize=(10, 6))
    for ext in extensions:
        plt.plot(
            [str(test_size) for test_size in test_sizes], file_sizes[ext], label=ext
        )
    plt.xlabel("Entry Size")
    plt.ylabel("File Size (KB)")
    plt.title("File Size by Format and Resolution")
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.savefig("plots/meta_sizes.png", dpi=300)
