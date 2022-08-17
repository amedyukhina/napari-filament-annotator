import numpy as np

from napari_filament_annotator import AnnotatorWidget


# make_napari_viewer is a pytest fixture that returns a napari viewer object
# capsys is a pytest fixture that captures stdout and stderr output streams
def test_annotator(make_napari_viewer, capsys, polygons):
    # make viewer and add an image layer using our fixture
    viewer = make_napari_viewer()

    # create annotator widget, passing in the viewer
    annotator = AnnotatorWidget(viewer)

    # call "add annotation layer" without image and assert no shape layers were added
    annotator.add_annotation_layer()
    assert annotator.annotation_layer_exists() is False

    # add an image
    viewer.add_image(np.random.random((10, 50, 50)))

    # call "add annotation layer" again and assert a new shape layer was added
    annotator.add_annotation_layer()
    assert annotator.annotation_layer_exists()
