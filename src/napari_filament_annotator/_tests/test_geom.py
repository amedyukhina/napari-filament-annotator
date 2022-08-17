import numpy as np

from napari_filament_annotator.utils.geom import tetragon_intersection, compute_polygon_intersection


def test_tetragon_intersection(tetragons):
    p1, p2 = tetragons
    inter = tetragon_intersection(p1, p2)
    assert inter is not None
    assert isinstance(inter, np.ndarray)
    assert inter.shape == (2, 3)


def test_polygon_intersection(polygons):
    x = compute_polygon_intersection(polygons)
    assert x is not None
    assert isinstance(x, np.ndarray)
    assert len(x.shape) == 2
    assert x.shape[1] == 3
