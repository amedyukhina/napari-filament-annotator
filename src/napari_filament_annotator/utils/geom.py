import numpy as np
from Geometry3D import *
from scipy.optimize import linear_sum_assignment
from scipy.spatial.distance import cdist


def tetragon_intersection(p1, p2):
    """
    Calculate intersection of two tetragons in 3D

    Parameters
    ----------
    p1, p2 : list or array
        List of tetragon coordinates of shape 4x3

    Returns
    -------
    list or None:
        List of (two) coordinate of the intersection line or None if no intersection exists.
    """
    p1 = np.array(p1)
    p2 = np.array(p2)
    if p1.shape != (4, 3) or p2.shape != (4, 3):
        raise ValueError("Input polygon shape must be (4, 3)")
    p1 = list(set([Point(*coords) for coords in p1]))
    p2 = list(set([Point(*coords) for coords in p2]))

    if len(p1) > 2 and len(p2) > 2:
        plane1 = ConvexPolygon(p1)
        plane2 = ConvexPolygon(p2)
        inter = intersection(plane1, plane2)
        if inter is not None:
            inter = np.array([list(pt) for pt in inter])
        return inter
    else:
        return None


def compute_polygon_intersection(polygons, spacing=None):
    """
    Compute intersection of two polygons.

    Parameters
    ----------
    polygons : tuple
        Two polygons, each specified by a list of near and far points.
        Each polygon must have shape 2 x N x 3,
            the first row representing the near points, and the second row representing the far points,
            N is the number of points, 3 is the dimension of the image.
    spacing : tuple, list or array
        Voxel size, (z, y, x).

    Returns
    -------
    np.ndarray of shape M x 3
        List of M points for the polygon intersection.
    """
    # near and far points of the both polygons
    npt1 = polygons[0][0]
    npt2 = polygons[1][0]
    fpt1 = polygons[0][1]
    fpt2 = polygons[1][1]

    # convert spacing
    if spacing is None:
        spacing = [1, 1, 1]
    spacing = np.array(spacing)

    # calculate intersections for each pair of tetragons that constitute the provided polygons
    intersections = []
    for i in range(len(npt1) - 1):
        for j in range(len(npt2) - 1):
            p1 = [npt1[i], npt1[i + 1], fpt1[i + 1], fpt1[i]]
            p2 = [npt2[j], npt2[j + 1], fpt2[j + 1], fpt2[j]]
            inter = tetragon_intersection(p1, p2)
            if inter is not None:
                intersections.append(inter)
            else:
                intersections.append(np.ones([2, 3]) * -1)  # set to -1 if no intersection exists

    # select the largest intersections
    intersections = np.array(intersections).reshape(len(npt1) - 1, len(npt2) - 1, 2, 3)
    l = np.sqrt(np.sum((intersections[:, :, 0] - intersections[:, :, 1]) ** 2, -1))  # length of each intersection
    inds = linear_sum_assignment(l, maximize=True)  # match tetragons based on the intersection length
    overlap = intersections[inds[0], inds[1]]
    overlap = np.array([o for o in overlap if np.min(o) >= 0])  # remove the pairs with no intersection (the -1 values)

    # the start and end of each segment are sometimes swapped
    # we replace the start and end points by the center of each segment
    # we also add the start of the first segment and the end of the last segment
    # to find these, we calculate distances between each pair of points and select those that are furthest apart
    centers = [(overlap[i][0] + overlap[i][1]) / 2
               for i in range(1, len(overlap) - 1)]  # center of each intersection segment (except the start and end)
    overlap = np.array(overlap).reshape(-1, 3)
    dist = cdist(overlap * spacing, overlap * spacing)  # distance between each pair of points
    ind = np.where(dist == dist.max())[0]  # select indices of points that are the furthest apart
    overlap = np.array([overlap[ind[0]]] +
                       centers +
                       [overlap[ind[1]]])  # furtherst points + centers of remaining intersections
    return overlap
