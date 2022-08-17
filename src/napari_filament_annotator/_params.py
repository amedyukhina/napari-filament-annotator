"""
Parameters for annotation display and refinement
"""

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

    def set_ac_parameters(self, n_iter=100, n_interp=5, end_coef=0.01, remove_corners=True):
        self.n_iter = n_iter
        self.n_interp = n_interp
        self.end_coef = end_coef
        self.remove_corners = remove_corners
