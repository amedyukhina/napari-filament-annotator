from typing import Union

import networkx as nx
import numpy as np
from scipy import ndimage
from skimage.filters import sobel
from skimage.restoration import ellipsoid_kernel
from sklearn.neighbors import NearestNeighbors


def get_derivatives(x):
    x = np.concatenate([x[:2][::-1], x, x[-2:][::-1]])
    d2 = np.roll(x, 1, 0) + np.roll(x, -1, 0) - 2 * x
    d4 = np.roll(x, 2, 0) - 4 * np.roll(x, 1, 0) + 6 * x - 4 * np.roll(x, -1, 0) + np.roll(x, -2, 0)
    return d2[2:-2], d4[2:-2]


def active_contour(img, snake, spacing=None, alpha=0.01, beta=0.1, gamma=1, n_iter=1000):
    if spacing is None:
        spacing = np.ones(img.ndim)
    grad = [sobel(img, axis=i) / spacing[i] for i in range(img.ndim)]
    for it in range(n_iter):
        coord = tuple(np.int_(np.round_(snake)).transpose())
        d2, d4 = get_derivatives(snake * spacing)
        fimg = np.array([grad[i][coord] for i in range(len(grad))])
        fimg = fimg / np.max(abs(fimg))
        fimg = - fimg.transpose()

        fsnake = d2 * 0 + d4 * beta
        fsnake = fsnake / np.max(abs(fsnake))
        force = fimg * gamma + fsnake
        force = force / np.max(abs(force))

        snake[1:-1] = snake[1:-1] - force[1:-1]
    return snake


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
