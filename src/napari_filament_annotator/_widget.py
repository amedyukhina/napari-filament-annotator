"""
3D Annotator Widget
"""

import napari
from napari.utils.notifications import show_info
from qtpy.QtWidgets import QVBoxLayout, QPushButton, QWidget, QMessageBox

from ._annotation import Annotation


class Annotator(QWidget):
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer
        self.annotation = None

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

            self.annotation = Annotation(self.viewer, self.viewer.layers[0])
            self.viewer = self.annotation.viewer
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
