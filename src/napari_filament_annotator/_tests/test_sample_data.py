import numpy as np
from napari_filament_annotator import load_sample_image


def test_sample_data():
    img = load_sample_image()
    assert isinstance(img, list)
    assert isinstance(img[0], tuple)
    assert isinstance(img[0][0], np.ndarray)
    assert len(img[0][0].shape) == 3
