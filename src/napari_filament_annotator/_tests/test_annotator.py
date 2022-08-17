import numpy as np

from napari_filament_annotator import AnnotatorWidget
from napari_filament_annotator._annotator import Annotator
from napari.utils.events import Event


# make_napari_viewer is a pytest fixture that returns a napari viewer object
# capsys is a pytest fixture that captures stdout and stderr output streams
def test_annotator(make_napari_viewer, capsys, polygons):
    # make viewer and add an image layer using our fixture
    viewer = make_napari_viewer()

    widget = AnnotatorWidget(viewer)
    viewer.add_image(np.random.random((12, 100, 100)))
    widget.add_annotation_layer()
    layer = widget.annotation_layer
    annotator = widget.annotator
    assert layer.nshapes == 1
    annotator.near_points = polygons[0][0].copy()
    annotator.far_points = polygons[0][1].copy()
    annotator.draw_polygon(layer)
    assert layer.nshapes == 2

    annotator.delete_the_last_point(layer)
    assert layer.nshapes == 2
    assert len(polygons[0][0]) == len(annotator.near_points) + 1 == len(annotator.far_points) + 1

    annotator.delete_the_last_shape(layer)
    assert layer.nshapes == 1

    annotator.near_points = polygons[0][0].copy()
    annotator.far_points = polygons[0][1].copy()
    assert len(annotator.near_points) > 0
    annotator.draw_polygon(layer)
    annotator.calculate_intersection(layer)
    assert layer.nshapes == 2
    assert len(annotator.polygons) == 1
    assert len(annotator.near_points) == len(annotator.far_points) == 0

    annotator.near_points = polygons[1][0].copy()
    annotator.far_points = polygons[1][1].copy()
    annotator.draw_polygon(layer)
    annotator.calculate_intersection(layer)
    assert layer.nshapes == 2
    assert len(widget.annotator.near_points) == len(widget.annotator.far_points) == len(widget.annotator.polygons) == 0
