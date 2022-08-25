"""
Parameters for annotation display and refinement
"""

import json
import os

import numpy as np


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

    def save(self, filename):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        params = dict(voxel_size_xy=self.scale[-1],
                      voxel_size_z=self.scale[0],
                      sigma_um=self.sigma[-1] * self.scale[-1],
                      line_width=self.line_width,
                      alpha=self.alpha,
                      beta=self.beta,
                      gamma=self.gamma,
                      n_iter=self.n_iter,
                      n_interp=self.n_interp,
                      end_coef=self.end_coef)
        with open(filename, 'w') as f:
            json.dump(params, f)
