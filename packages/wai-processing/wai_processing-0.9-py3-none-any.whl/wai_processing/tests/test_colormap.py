import argparse
import os

import matplotlib.patches as patches
from matplotlib import pyplot as plt

from wai.semantics import load_semantic_color_mapping

parser = argparse.ArgumentParser(description="Colormap visualization")
parser.add_argument(
    "--fname",
    type=str,
    default="colors_fps_5k.npz",
    help="Filename of the colormap, located in the 'wai/colormap' directory.",
)
parser.add_argument(
    "--num_colors",
    type=int,
    default=150,
    help="Number of colors to plot, starting from the first color in the colormap.",
)


if __name__ == "__main__":
    args = parser.parse_args()
    colors = load_semantic_color_mapping(args.fname)

    fig, ax = plt.subplots(figsize=(10, 2))
    ax.set_xlim(0, args.num_colors)
    ax.set_ylim(0, 1)
    ax.axis("off")
    for i in range(args.num_colors):
        rect = patches.Rectangle((i, 0), 1, 1, facecolor=tuple(colors[i] / 255.0))
        ax.add_patch(rect)

    cmap_name = os.path.splitext(args.fname)[0]
    plt.title(f"First {args.num_colors} colors of {args.fname}", fontsize=10)
    plt.tight_layout()
    plt.savefig(f"{cmap_name}_first_{args.num_colors}.png", dpi=300)
