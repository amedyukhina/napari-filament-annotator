"""
This module is an example of a barebones sample data provider for napari.

It implements the "sample data" specification.
see: https://napari.org/plugins/guides.html?#sample-data

Replace code below according to your needs.
"""
from __future__ import annotations

from skimage import io


def load_sample_image():
    img = io.imread("https://github.com/amedyukhina/napari-filament-annotator/raw/main/img/example_image.tif")
    return [(img, {})]
