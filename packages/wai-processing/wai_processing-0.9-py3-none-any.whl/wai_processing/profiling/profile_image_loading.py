import functools
import os
import timeit

import cv2
import imageio
import matplotlib.pyplot as plt
import torch
import torchvision.transforms as transforms
from PIL import Image
from torchvision.io import read_image
from tqdm import tqdm


# Function to load image using PIL and convert to tensor
def load_image_pil(image_name):
    with Image.open(image_name) as img:
        tensor = transforms.ToTensor()(img)
    return tensor


# Function to load image using imageio and convert to tensor
def load_image_imageio(image_name):
    return torch.from_numpy(imageio.imread(image_name)).permute(2, 0, 1).float() / 255.0


# Function to load image using OpenCV and convert to tensor
def load_image_opencv(image_name):
    img = cv2.imread(image_name)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB
    tensor = torch.from_numpy(img).permute(2, 0, 1).float() / 255.0
    return tensor


# Function to load image using torchvision's native read_image
def load_image_torchvision(image_name):
    tensor = read_image(image_name).float() / 255.0
    return tensor


# Profiling
test_resolutions = [(2**i, 2**i) for i in range(7, 14)]
STORE_ROOT = "test_data/color_images"
methods = ["pil", "opencv", "torchvision", "imageio"]
extensions = ["png", "jpg"]
loading_times = {f"{method}-{ext}": [] for method in methods for ext in extensions}
for test_res in tqdm(test_resolutions, "Loading images"):
    for ext in extensions:
        fn = f"{STORE_ROOT}/res_{test_res[0]:04}x{test_res[1]:04}.{ext}"
        for method in methods:
            if method == "pil":
                loading_time = timeit.timeit(
                    functools.partial(load_image_pil, fn), number=5
                )
            elif method == "opencv":
                loading_time = timeit.timeit(
                    functools.partial(load_image_opencv, fn), number=5
                )
            elif method == "torchvision":
                loading_time = timeit.timeit(
                    functools.partial(load_image_torchvision, fn), number=5
                )
            elif method == "imageio":
                loading_time = timeit.timeit(
                    functools.partial(load_image_imageio, fn), number=5
                )
            else:
                raise NotImplementedError
            loading_times[f"{method}-{ext}"].append(1000 * loading_time)  # ms

# Plot file sizes
plt.figure(figsize=(10, 6))
for method in methods:
    for ext in extensions:
        plt.plot(
            [f"{res[0]}x{res[1]}" for res in test_resolutions],
            loading_times[f"{method}-{ext}"],
            label=f"{method}-{ext}",
        )
plt.xlabel("Image resolution")
plt.ylabel("Loading time (ms)")
plt.title("Loading time by Method and Resolution")
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
os.makedirs("plots", exist_ok=True)
plt.savefig("plots/image_loading.png", dpi=300)
