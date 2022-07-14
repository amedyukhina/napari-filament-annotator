"""
3D Annotator Widget
"""
import itertools

import napari
import numpy as np
from napari.utils.notifications import show_info
from qtpy.QtWidgets import QVBoxLayout, QPushButton, QWidget, QMessageBox


class Annotator(QWidget):
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer
        self.annotation_layer = None

        btn = QPushButton("Add annotation layer")
        btn.clicked.connect(self.add_annotation_layer)
        layout = QVBoxLayout()
        layout.addWidget(btn)

        self.setLayout(layout)

    def add_annotation_layer(self):
        """
        Add an annotation layer to the napari viewer.
        """
        if len(self.viewer.layers) > 0 and isinstance(self.viewer.layers[0], napari.layers.Image):
            if len(self.get_shape_layers()) > 0:
                answer = self._confirm_adding_second_layer()
                if answer == QMessageBox.No:
                    return
            shape = self.viewer.layers[0].data.shape

            # add a bounding box to set the coordinates range
            bbox = list(itertools.product(*[np.arange(2)
                                            for i in range(len(shape[-3:]))]))
            if len(shape) > 3:
                bbox = [(0,) + b for b in bbox]
            bbox = bbox * np.array(shape)

            self.annotation_layer = self.viewer.add_shapes(bbox,
                                                           name='annotations',
                                                           shape_type='path',
                                                           edge_width=0,
                                                           scale=self.viewer.layers[0].scale
                                                           )
        else:
            show_info("No images open! Please open an image first")

    def get_shape_layers(self):
        return [layer for layer in self.viewer.layers if isinstance(layer, napari.layers.Shapes)]

    def _confirm_adding_second_layer(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)

        msg.setWindowTitle("Annotation layer already exists")
        msg.setText("Annotation layer already exists! Are you sure you want to add another annotation layer?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        return msg.exec_()
