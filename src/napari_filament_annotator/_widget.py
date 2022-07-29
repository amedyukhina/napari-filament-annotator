"""
3D Annotator Widget
"""
import itertools
from pathlib import Path

import napari
import numpy as np
import pandas as pd
from magicgui import magicgui
from magicgui.widgets import Container
from napari.utils.notifications import show_info
from qtpy.QtWidgets import QVBoxLayout, QPushButton, QWidget, QMessageBox

from ._annotation import annotate_filaments
from .utils.io import annotation_to_pandas


class Params():
    def __init__(self, scale, line_width=1, sigma_um=0.5, alpha=0.01, beta=0.1, gamma=1, n_iter=100):
        self.scale = np.array(scale)
        self.line_width = line_width
        self.sigma = sigma_um / self.scale
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.n_iter = n_iter

    def update_parameters(self, line_width=1, sigma_um=0.5, alpha=0.01, beta=0.1, gamma=1, n_iter=100):
        self.line_width = line_width
        self.sigma = sigma_um / self.scale
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.n_iter = n_iter


class Annotator(QWidget):
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer
        self.viewer.dims.ndisplay = 3
        self.annotation_layer = None

        self.scale_params()
        self.params = Params(self.scale)
        self.parameters()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Voxe size and annotation parameters
        self.w = Container(widgets=[magicgui(self.scale_params, layout='vertical', auto_call=True),
                                    magicgui(self.parameters, layout='vertical', auto_call=True)],
                           labels=None)
        self.add_magic_function(self.w, layout)

        # "Add annotation layer" button
        btn = QPushButton("Add annotation layer")
        btn.clicked.connect(self.add_annotation_layer)
        layout.addWidget(btn)

        # File dialog
        self.sw = magicgui(self.annotation_filename, layout='vertical', auto_call=True,
                           filename={"mode": "w", "label": "Choose output CSV file:", "filter": "*.csv"})
        self.add_magic_function(self.sw, layout)

        # "Save annotation" button
        btn_save = QPushButton("Save annotations")
        btn_save.clicked.connect(self.save_annotations)
        layout.addWidget(btn_save)

    def annotation_filename(self, filename=Path("annotations.csv")):
        self.filename = filename

    def save_annotations(self):
        if self.annotation_layer is not None and self.annotation_layer.nshapes > 1:
            annotation_to_pandas(self.annotation_layer.data[1:]).to_csv(self.filename, index=False)
        else:
            pd.DataFrame().to_csv(self.filename, index=False)
        print(rf"Saved to: {self.filename}")

    def add_magic_function(self, function, _layout):
        self.viewer.layers.events.inserted.connect(function.reset_choices)
        self.viewer.layers.events.removed.connect(function.reset_choices)
        _layout.addWidget(function.native)

    def set_scale(self, scale):
        self.scale = scale
        if np.min(scale) > 0:
            for i in range(len(self.viewer.layers)):
                self.viewer.layers[i].scale = scale
            self.viewer.dims.ndisplay = 2
            self.viewer.dims.ndisplay = 3

    def scale_params(self, voxel_size_xy: float = 0.1, voxel_size_z: float = 0.2):
        """
        Specify voxel size.

        Parameters
        ----------
        voxel_size_xy : float
            Voxel size in xy (microns)
        voxel_size_z : float
            Voxel size in z (microns)
        """
        self.set_scale([voxel_size_z, voxel_size_xy, voxel_size_xy])

    def parameters(self, line_width: float = 1., sigma_um: float = 0.5,
                   alpha=0.01, beta=0.1, gamma=1, n_iter=100):
        """

        Parameters
        ----------
        line_width : float
            Width of the annotation lines in the viewer.
        sigma_um : flaot
            Gaussian sigma (in microns) to smooth the image for identifying the brightest neighborhood point.
        alpha : float
            Active contour weight for the first derivative
        beta : float
            Active contour weight for the seconf derivative
        gamma : float
            Active contour weight for the image contribution
        n_iter : int
            Number of iterations of the active contour

        """

        self.params.update_parameters(sigma_um=sigma_um, line_width=line_width,
                                      alpha=alpha, beta=beta, gamma=gamma, n_iter=n_iter)

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
            annotate_filaments(self.annotation_layer, params=self.params,
                               image_layer=self.viewer.layers[0])

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
