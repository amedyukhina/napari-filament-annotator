from __future__ import annotations

from skimage import io


def load_sample_image():
    img = io.imread("https://github.com/amedyukhina/napari-filament-annotator/raw/main/img/example_image.tif")
    return [(img, {})]
