"""
3D AnnotatorWidget Widget
"""
import argparse
import json
import os
from pathlib import Path

import napari
import numpy as np
import pandas as pd
from magicgui import magicgui
from napari.utils.notifications import show_info
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QMessageBox, QLabel, QSlider

from ._annotator import Annotator
from ._params import Params
from .utils.io import annotation_to_pandas, pandas_to_annotations

TEXT_PROP = {
    'text': 'label',
    'anchor': 'upper_left',
    'translation': [2, 2, 5],
    'size': 7,
    'color': 'green'
}


class AnnotatorWidget(QWidget):
    """
    Annotator Widget
    """

    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer
        self.annotation_layer = None
        image_layer = self.get_image_layer()
        self.image = image_layer.data if image_layer is not None else None
        path = image_layer.source.path if image_layer is not None else None
        self.datapath = os.path.dirname(path) if path is not None else '.'
        self.filename = path[:-len(path.split('.')[-1]) - 1] + '.csv' if path is not None else 'annotations.csv'
        self.param_filename = os.path.join(self.datapath, 'params.json') if path is not None else 'params.json'
        self.params = Params()
        self.set_params()
        self.setup_ui()

    def set_params(self):
        """Set annotation parameters"""
        self.voxel_params()
        self.sigma_param()
        self.display_params()
        self.ac_parameters1()
        self.ac_parameters2()

    def voxel_params(self, voxel_size_xy: float = 0.1, voxel_size_z: float = 0.1):
        """
        Specify voxel size.

        Parameters
        ----------
        voxel_size_xy : float
            Voxel size in xy (microns)
        voxel_size_z : float
            Voxel size in z (microns)
        """
        self._set_scale([voxel_size_z, voxel_size_xy, voxel_size_xy])
        self.params.set_scale(self.scale)

    def sigma_param(self, sigma_um: float = 0.2):
        """
        Specify voxel size.

        Parameters
        ----------
        sigma_um : flaot
            Gaussian sigma (in microns) to smooth the image for active contour refinement.
        """
        self.params.set_smoothing(sigma_um)

    def display_params(self, line_width: float = 0.5):
        """

        Parameters
        ----------
        line_width : float
            Width of the annotation lines in the viewer.
        """
        self.params.set_linewidth(line_width)

    def ac_parameters1(self, alpha: float = 0.01, beta: float = 0.1, gamma: float = 1):
        """

        Parameters
        ----------
        alpha : float
            Active contour weight for the first derivative
        beta : float
            Active contour weight for the second derivative
        gamma : float
            Active contour weight for the image contribution
        """
        self.params.set_coef(alpha=alpha, beta=beta, gamma=gamma)

    def ac_parameters2(self, n_iter: int = 1000, n_interp: int = 3, end_coef: float = 0.0):
        """

        Parameters
        ----------
        n_iter : int
            Number of iterations of the active contour
            Width of the annotation lines in the viewer.
        n_interp : int
            Number of points to interpolate between each pair of annotated point
        end_coef : float
            Coefficient (between 0 and 1) to scale the forces applied to the contour end points.
            Set to 0 to fix the end points.
        """
        self.params.set_ac_parameters(n_iter=n_iter, n_interp=n_interp,
                                      end_coef=end_coef)

    def load_annotations(self, filename=Path('.')):
        """

        Parameters
        ----------
        filename : Path
            Filename to load annoations

        """
        df = pd.read_csv(filename)
        data, labels = pandas_to_annotations(df)
        self.viewer.add_shapes(data, name='existing_annotations',
                               shape_type='path', edge_color='green',
                               edge_width=self.params.line_width,
                               scale=self.viewer.layers[0].scale,
                               blending='additive',
                               properties={'label': labels}, text=TEXT_PROP)
        if not self.annotation_layer_exists():
            self.add_annotation_layer()
        self.annotation_layer.add(data, shape_type='path', edge_color='green',
                                  edge_width=self.params.line_width)

    def load_parameters(self, filename=Path('.')):
        """

        Parameters
        ----------
        filename : Path
            Filename to load parameters

        """
        with open(filename, 'r') as f:
            params = json.load(f)
        params = argparse.Namespace(**params)
        self.magic_voxel_params.voxel_size_xy.value = params.voxel_size_xy
        self.magic_voxel_params.voxel_size_z.value = params.voxel_size_z
        self.magic_sigma_param.sigma_um.value = params.sigma_um
        self.magic_display_params.line_width.value = params.line_width
        self.magic_ac_parameters1.alpha.value = params.alpha
        self.magic_ac_parameters1.beta.value = params.beta
        self.magic_ac_parameters1.gamma.value = params.gamma
        self.magic_ac_parameters2.n_iter.value = params.n_iter
        self.magic_ac_parameters2.n_interp.value = params.n_interp
        self.magic_ac_parameters2.end_coef.value = params.end_coef

    def get_param_filename(self, filename=Path('.')):
        """

        Parameters
        ----------
        filename : Path
            Filename to save parameters
        """
        self.param_filename = filename
        self.save_parameters()

    def save_parameters(self):
        self.params.save(self.param_filename)
        print(rf"Saved to: {self.param_filename}")

    def get_annotation_filename(self, filename=Path('.')):
        """

        Parameters
        ----------
        filename : Path
            Filename to save annotations
        """
        self.filename = filename
        self.save_annotations()

    def save_annotations(self):
        if self.annotation_layer is not None and self.annotation_layer.nshapes > 1:
            annotation_to_pandas(self.annotation_layer.data[1:]).to_csv(self.filename, index=False)
        else:
            pd.DataFrame().to_csv(self.filename, index=False)
        print(rf"Saved to: {self.filename}")

    def set_maxval(self):
        maxval = self.sld.value()
        img_layer = self.get_image_layer()
        if img_layer is not None:
            if self.image is None:
                self.image = img_layer.data
                self.sld.setMaximum(self.image.max())
            img_layer.data = np.where(self.image > maxval, 0, self.image)

    def get_image_layer(self):
        if len(self.viewer.layers) > 0 and isinstance(self.viewer.layers[0], napari.layers.Image):
            return self.viewer.layers[0]
        else:
            return None

    def annotation_layer_exists(self):
        """
        Check if the annotation layer still exists in the viewer.
        The self.annotation_layer variable will not get updated if the layer is deleted from the viewer.
        """
        return len([layer for layer in self.viewer.layers
                    if isinstance(layer, napari.layers.Shapes) and layer.name == 'annotations']) > 0

    def add_annotation_layer(self):
        """
        Add an annotation layer to the napari viewer.
        """
        img_layer = self.get_image_layer()
        self.viewer.dims.ndisplay = 3
        if img_layer is not None:
            if self.annotation_layer_exists():
                answer = self._confirm_adding_second_layer()
                if answer == QMessageBox.No:
                    return
            if len(img_layer.data.shape) == 3:
                self.annotator = Annotator(self.viewer, img_layer, self.params)
                self.annotation_layer = self.annotator.annotation_layer
            else:
                show_info("Only 3D gray-scale images are currently supported! "
                          rf"The current image has {len(img_layer.data.shape)} dimensions.")
        else:
            show_info("No images open! Please open an image first")

    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Load parameters from file
        self._add_magic_function(magicgui(self.load_parameters, layout='vertical', auto_call=True,
                                          filename={"mode": "r",
                                                    "label": "Load existing parameters:",
                                                    "filter": "*.json",
                                                    "value": self.param_filename}),
                                 layout)

        # Voxe size and annotation parameters
        l1 = QHBoxLayout()
        l1.addWidget(QLabel("Image parameters"))
        layout.addLayout(l1)
        self.magic_sigma_param = magicgui(self.sigma_param, layout='vertical', auto_call=True)
        self._add_magic_function(self.magic_sigma_param, l1)
        self.magic_voxel_params = magicgui(self.voxel_params, layout='vertical', auto_call=True)
        self._add_magic_function(self.magic_voxel_params, layout)

        # Slider for masking out spindle
        l2 = QHBoxLayout()
        layout.addLayout(l2)
        l2.addWidget(QLabel("Mask out bright pixels"))
        self.sld = QSlider(Qt.Horizontal)
        self.sld.valueChanged.connect(self.set_maxval)
        img_layer = self.get_image_layer()
        if img_layer is not None:
            self.sld.setMaximum(img_layer.data.max())
            self.sld.setValue(img_layer.data.max())
        self.sld.setValue(self.sld.maximum())
        l2.addWidget(self.sld, Qt.Horizontal)
        self.set_maxval()

        # "Add annotation layer" button
        btn = QPushButton("Add annotation layer")
        btn.clicked.connect(self.add_annotation_layer)
        layout.addWidget(btn)

        # Display parameters
        l3 = QHBoxLayout()
        layout.addLayout(l3)
        l3.addWidget(QLabel("Display parameters"))
        self.magic_display_params = magicgui(self.display_params, layout='vertical', auto_call=True)
        self._add_magic_function(self.magic_display_params, l3)

        # Active contour parameters
        layout.addWidget(QLabel("Active contour parameters"))
        l4 = QHBoxLayout()
        layout.addLayout(l4)

        self.magic_ac_parameters1 = magicgui(self.ac_parameters1, layout='vertical', auto_call=True)
        self.magic_ac_parameters2 = magicgui(self.ac_parameters2, layout='vertical', auto_call=True)
        self._add_magic_function(self.magic_ac_parameters1, l4)
        self._add_magic_function(self.magic_ac_parameters2, l4)

        # Save parameters
        l5 = QHBoxLayout()
        layout.addLayout(l5)
        self._add_magic_function(magicgui(self.get_param_filename, layout='vertical', auto_call=True,
                                          filename={"mode": "w",
                                                    "label": "Save parameters:",
                                                    "filter": "*.json",
                                                    "value": self.param_filename}),
                                 l5)
        btn_save = QPushButton("Save parameters")
        btn_save.clicked.connect(self.save_parameters)
        l5.addWidget(btn_save)

        # Load annotations
        l6 = QHBoxLayout()
        layout.addLayout(l6)
        self._add_magic_function(magicgui(self.load_annotations, layout='vertical', auto_call=True,
                                          filename={"mode": "r",
                                                    "label": "Load existing annotations:",
                                                    "filter": "*.csv",
                                                    "value": self.datapath}),
                                 l6)

        # Save annotations
        l7 = QHBoxLayout()
        layout.addLayout(l7)
        self._add_magic_function(magicgui(self.get_annotation_filename, layout='vertical', auto_call=True,
                                          filename={"mode": "w",
                                                    "label": "Save annotations:",
                                                    "filter": "*.csv",
                                                    "value": self.filename}),
                                 l7)
        btn_save = QPushButton("Save annotations")
        btn_save.clicked.connect(self.save_annotations)
        l7.addWidget(btn_save)

    def _set_scale(self, scale):
        self.scale = scale
        if np.min(scale) > 0:
            for i in range(len(self.viewer.layers)):
                self.viewer.layers[i].scale = scale
            self.viewer.dims.ndisplay = 2
            self.viewer.dims.ndisplay = 3

    def _add_magic_function(self, function, _layout):
        # self.viewer.layers.events.inserted.connect(function.reset_choices)
        # self.viewer.layers.events.removed.connect(function.reset_choices)
        _layout.addWidget(function.native)

    def _confirm_adding_second_layer(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)

        msg.setWindowTitle("Annotation layer already exists")
        msg.setText("Annotation layer already exists! Are you sure you want to add another annotation layer?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        return msg.exec_()
