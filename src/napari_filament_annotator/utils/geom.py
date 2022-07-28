import numpy as np
from Geometry3D import *
from scipy.optimize import linear_sum_assignment
from scipy.spatial.distance import cdist


def tetragon_intersection(p1: list, p2: list):
    """
    Calculate intersection of two tetragons in 3D

    Parameters
    ----------
    p1, p2 : list
        List of tetragon coordinates

    Returns
    -------
    list or None:
        List of (two) coordinate of the intersection line or None if no intersection exists.
    """
    t = []
    p1 = np.array(p1)
    p2 = np.array(p2)
    if p1.shape[1] > 3:
        t = list(p1[0][:-3])
        p1 = p1[:, -3:]
        p2 = p2[:, -3:]
    p1 = list(set([Point(*coords) for coords in p1]))
    p2 = list(set([Point(*coords) for coords in p2]))

    if len(p1) > 2 and len(p2) > 2:
        plane1 = ConvexPolygon(p1)
        plane2 = ConvexPolygon(p2)
        inter = intersection(plane1, plane2)
        if inter is not None:
            inter = [t + list(pt) for pt in inter]
        return inter
    else:
        return None


def compute_polygon_intersection(polygons, spacing):
    npt1 = polygons[0][0]
    npt2 = polygons[1][0]
    fpt1 = polygons[0][1]
    fpt2 = polygons[1][1]
    mt = []

    intersections = []
    mask = []
    for i in range(len(npt1) - 1):
        for j in range(len(npt2) - 1):
            p1 = [npt1[i], npt1[i + 1], fpt1[i + 1], fpt1[i]]
            p2 = [npt2[j], npt2[j + 1], fpt2[j + 1], fpt2[j]]
            inter = tetragon_intersection(p1, p2)
            if inter is not None:
                intersections.append(inter)
                mask.append(1)
            else:
                intersections.append(np.ones([2, 3]) * -1)
                mask.append(0)
    intersections = np.array(intersections).reshape(len(npt1) - 1, len(npt2) - 1, 2, 3)
    l = np.sqrt(np.sum((intersections[:, :, 0] - intersections[:, :, 1]) ** 2, -1))
    inds = linear_sum_assignment(l, maximize=True)
    mt = intersections[inds[0], inds[1]]
    mtcenter = [(mt[i][0] + mt[i][1]) / 2 for i in range(1, len(mt) - 1)]
    mt = np.array(mt).reshape(-1, 3)
    dist = cdist(mt * spacing, mt * spacing)
    ind = np.where(dist == dist.max())[0]
    mt = np.array([mt[ind[0]]] + mtcenter + [mt[ind[1]]])
    return mt
