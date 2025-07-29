import os
import pathlib
import random
import shutil
import sys
import time
from glob import glob
from turtle import mode
from urllib.parse import urlparse

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import skimage.io
from cellpose import core, io, metrics, models, plot, utils
from deepcell.applications import Mesmer
from deepcell.utils.plot_utils import create_rgb_image, make_outline_overlay
from skimage import exposure
from skimage.color import rgb2gray
from skimage.measure import regionprops_table
from tensorflow.keras.models import load_model
from tqdm import tqdm


def overlay_masks_on_image(image, masks, gamma=1.5):
    # Convert image to grayscale
    gray_image = rgb2gray(image)

    # Increase brightness using gamma correction
    # Adjust the gamma value as needed
    gray_image = exposure.adjust_gamma(gray_image, gamma=gamma)

    # Convert grayscale to RGB to overlay the masks
    overlay = np.stack([gray_image] * 3, axis=-1)

    outlines = utils.masks_to_outlines(masks)

    # Overlay the mask as red outlines on the grayscale image
    overlay[outlines == 1] = [255, 0, 0]

    return overlay, gray_image


def check_segmentation(overlay, grayscale, n=10, tilesize=1000):
    # Check the shapes of provided arrays
    # if overlay.shape != grayscale.shape:
    #    raise ValueError("The two images should have the same shape")

    # Calculate the number of tiles in x and y directions
    y_tiles, x_tiles = overlay.shape[0] // tilesize, overlay.shape[1] // tilesize

    # Split images into tiles
    overlay_tiles = []
    grayscale_tiles = []
    for i in range(x_tiles):
        for j in range(y_tiles):
            x_start, y_start = i * tilesize, j * tilesize
            overlay_tile = overlay[
                y_start : y_start + tilesize, x_start : x_start + tilesize
            ]
            grayscale_tile = grayscale[
                y_start : y_start + tilesize, x_start : x_start + tilesize
            ]
            overlay_tiles.append(overlay_tile)
            grayscale_tiles.append(grayscale_tile)

    # Randomly select n tiles
    random_indices = random.sample(range(len(overlay_tiles)), n)

    # Plot the tiles
    fig, axs = plt.subplots(n, 2, figsize=(10, 5 * n))
    for i, idx in enumerate(random_indices):
        axs[i, 0].imshow(overlay_tiles[idx])
        axs[i, 0].axis("off")
        axs[i, 1].imshow(grayscale_tiles[idx], cmap="gray")
        axs[i, 1].axis("off")
    plt.tight_layout()
    plt.show()
