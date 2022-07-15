from typing import Union

import networkx as nx
import numpy as np
from scipy import ndimage
from skimage.restoration import ellipsoid_kernel
from sklearn.neighbors import NearestNeighbors


def __gaussian_kernel(sigma, shape):
    kernel = np.zeros(shape)
    kernel[tuple(np.int_((np.array(shape) - 1) / 2))] = 255.
    kernel = ndimage.gaussian_filter(kernel, sigma)
    kernel = kernel / np.max(kernel)
    return kernel


def sort_points(points):
    points = np.array(points)

    # calculate distance matrix
    nbr = NearestNeighbors(n_neighbors=len(points)).fit(points)
    distances, indices = nbr.kneighbors(points)

    # build a graph with distances as edges
    G = nx.Graph()
    G.add_weighted_edges_from([(i, indices[i, j], distances[i, j])
                               for i in range(len(points)) for j in range(len(points))])

    # calculate the shortest path as the Traveling Salesman Problem
    path = nx.approximation.traveling_salesman_problem(G, weight='weight', cycle=False)

    return points[path]


def snap_to_brightest(points: Union[list, np.ndarray], img: np.ndarray, rad: Union[int, list, np.ndarray] = 5,
                      decay_sigma: Union[int, float, list, np.ndarray] = 5.):
    """
    Snap the filament points to the brightest point in the image in the give neighborhood.

    Parameters
    ----------
    points : list
        List of filament coordinates.
    img : np.ndarray
        Image used to find the brightest point.
    rad : int or sequence, optional
        Radius of the neighborhood (in pixels) to consider for identifying the brightest points.
        Can be provided as a list of values for different dimensions.
        Default is 5.
    decay_sigma : scalar or sequence, optional
        Sigma of a Gaussian used to scale image intensities centered on the original annotated point.
        This is done to give preference to the original point, if there are other points with the same intensity.
        Default is 5.
    Returns
    -------

    """
    rad = np.ravel(rad)
    if len(rad) < len(img.shape):
        rad = np.array([rad[0]] * len(img.shape))
    decay_sigma = np.ravel(decay_sigma)
    if len(decay_sigma) < len(img.shape):
        decay_sigma = np.array([decay_sigma[0]] * len(img.shape))
    kernel = (ellipsoid_kernel(rad * 2 + 1, 1) < 1) * 1
    imgpad = np.pad(img, [(r + 1, r + 1) for r in rad])
    points = np.int_(np.round_(points))

    updated_points = []
    for point in points:
        sl = [slice(point[i] + 1, point[i] + 2 * rad[i] + 2) for i in range(len(point))]
        crop = imgpad[tuple(sl)] * kernel * __gaussian_kernel(decay_sigma, kernel.shape)
        shift = np.array(np.where(crop == np.max(crop))).transpose()[0] - rad
        updated_points.append(np.array(point) + shift)
    return np.array(updated_points)
