"""
3D Annotator Widget
"""
import itertools
import os
from pathlib import Path

import napari
import numpy as np
import pandas as pd
from magicgui import magicgui
from napari.utils.notifications import show_info
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QMessageBox, QLabel, QSlider

from ._annotation import annotate_filaments
from .utils.io import annotation_to_pandas, pandas_to_annotations


class Params():

    def set_scale(self, scale):
        self.scale = np.array(scale)

    def set_smoothing(self, sigma_um):
        self.sigma = sigma_um / self.scale

    def set_linewidth(self, line_width):
        self.line_width = line_width

    def set_coef(self, alpha=0.01, beta=0.1, gamma=1):
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma

    def set_ac_parameters(self, n_iter=100, n_interp=5, end_coef=0.01):
        self.n_iter = n_iter
        self.n_interp = n_interp
        self.end_coef = end_coef


class Annotator(QWidget):
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer
        self.viewer.dims.ndisplay = 3
        self.annotation_layer = None
        image_layer = self.get_image_layer()
        self.image = image_layer.data if image_layer is not None else None
        self.datapath = os.path.dirname(image_layer.source.path) if image_layer is not None else '.'
        self.filename = image_layer.source.path[:-len(image_layer.source.path.split('.')[-1]) - 1] + '.csv' \
            if image_layer is not None else 'annotations.csv'
        self.params = Params()
        self.set_params()
        self.setup_ui()

    def set_params(self):
        self.voxel_params()
        self.sigma_param()
        self.display_params()
        self.ac_parameters1()
        self.ac_parameters2()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Voxe size and annotation parameters
        l1 = QHBoxLayout()
        layout.addLayout(l1)
        l1.addWidget(QLabel("Image parameters"))
        self.add_magic_function(magicgui(self.sigma_param, layout='vertical', auto_call=True), l1)
        self.add_magic_function(magicgui(self.voxel_params, layout='horizontal', auto_call=True), layout)

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
        self.add_magic_function(magicgui(self.display_params, layout='vertical', auto_call=True), l3)

        # Active contour parameters
        layout.addWidget(QLabel("Active contour parameters"))
        l4 = QHBoxLayout()
        layout.addLayout(l4)
        self.add_magic_function(magicgui(self.ac_parameters1, layout='vertical', auto_call=True), l4)
        self.add_magic_function(magicgui(self.ac_parameters2, layout='vertical', auto_call=True), l4)

        # # Annotation table
        # layout.addWidget(QLabel("Current annotations"))
        # self.table = QTableWidget()
        # self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        # self.table.setRowCount(3)
        # self.table.setColumnCount(10)
        #
        # for i in range(10):
        #     self.table.setHorizontalHeaderItem(i, QTableWidgetItem(str(i)))
        #     for j in range(3):
        #         self.table.setItem(j, i, QTableWidgetItem(str(j)))
        # layout.addWidget(self.table)

        # Open file dialog
        l5 = QHBoxLayout()
        layout.addLayout(l5)
        self.add_magic_function(magicgui(self.load_annotations, layout='vertical', auto_call=True,
                                         filename={"mode": "r",
                                                   "label": "Load existing annotations:",
                                                   "filter": "*.csv",
                                                   "value": self.datapath}),
                                l5)

        # Save file dialog
        l6 = QHBoxLayout()
        layout.addLayout(l6)
        self.add_magic_function(magicgui(self.annotation_filename, layout='vertical', auto_call=True,
                                         filename={"mode": "w",
                                                   "label": "Output CSV file:",
                                                   "filter": "*.csv",
                                                   "value": self.filename}),
                                l6)
        btn_save = QPushButton("Save annotations")
        btn_save.clicked.connect(self.save_annotations)
        l6.addWidget(btn_save)

    def set_maxval(self):
        maxval = self.sld.value()
        img_layer = self.get_image_layer()
        if img_layer is not None:
            if self.image is None:
                self.image = img_layer.data
                self.sld.setMaximum(self.image.max())
            self.viewer.dims.ndisplay = 2
            img_layer.data = np.where(self.image > maxval, 0, self.image)

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

    def voxel_params(self, voxel_size_xy: float = 0.035, voxel_size_z: float = 0.140):
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
        self.params.set_scale(self.scale)

    def sigma_param(self, sigma_um: float = 0.05):
        """
        Specify voxel size.

        Parameters
        ----------
        sigma_um : flaot
            Gaussian sigma (in microns) to smooth the image for identifying the brightest neighborhood point.
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
            Active contour weight for the seconf derivative
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
            Number of points to interpolate between each annotated point
        end_coef : float
            Coefficient (between 0 and 1) to scale the forces applied to the contour end points.
            Set to 0 to fix the end points.
        """
        self.params.set_ac_parameters(n_iter=n_iter, n_interp=n_interp, end_coef=end_coef)

    def get_image_layer(self):
        if len(self.viewer.layers) > 0 and isinstance(self.viewer.layers[0], napari.layers.Image):
            return self.viewer.layers[0]
        else:
            return None

    def add_annotation_layer(self):
        """
        Add an annotation layer to the napari viewer.
        """
        img_layer = self.get_image_layer()
        self.viewer.dims.ndisplay = 3
        if img_layer is not None:
            if len(self.get_shape_layers()) > 0:
                answer = self._confirm_adding_second_layer()
                if answer == QMessageBox.No:
                    return

            shape = img_layer.data.shape

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
                                                           scale=self.viewer.layers[0].scale,
                                                           blending='additive'
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

    def annotation_filename(self, filename=Path('.')):
        self.filename = filename
        self.save_annotations()

    def load_annotations(self, filename=Path('.')):
        df = pd.read_csv(filename)
        data = pandas_to_annotations(df)
        if self.annotation_layer is None:
            self.add_annotation_layer()
        self.annotation_layer.add(data, shape_type='path', edge_color='green',
                                  edge_width=self.params.line_width)

    def save_annotations(self):
        if self.annotation_layer is not None and self.annotation_layer.nshapes > 1:
            annotation_to_pandas(self.annotation_layer.data[1:]).to_csv(self.filename, index=False)
        else:
            pd.DataFrame().to_csv(self.filename, index=False)
        print(rf"Saved to: {self.filename}")
