import numpy as np
from Geometry3D import *


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


def compute_polygon_intersection(npt1: np.ndarray, npt2: np.ndarray,
                                 fpt1: np.ndarray, fpt2: np.ndarray):
    """
    Calculate intersection of two non-convex polygons represented by a list of near and far points.

    Parameters
    ----------
    npt1 : np.ndarray
        Near points of the first polygon.
    npt2 : np.ndarray
        Near points of the second polygon.
    fpt1 : np.ndarray
        Far points of the first polygon.
    fpt2 : np.ndarray
        Far points of the second polygon.
    Returns
    -------
    np.ndarray:
        n x d array of the intersections coordinates,
        where n is the number of points, d is the number of dimensions.
    """
    mt = []

    for i in range(len(npt1) - 1):
        for j in range(len(npt2) - 1):
            p1 = [npt1[i], npt1[i + 1], fpt1[i + 1], fpt1[i]]
            p2 = [npt2[j], npt2[j + 1], fpt2[j + 1], fpt2[j]]
            inter = tetragon_intersection(p1, p2)
            if inter is not None:
                if len(mt) == 0:
                    mt = inter
                else:
                    mt = np.concatenate([mt, inter], axis=0)

    mt = np.array(list(set([tuple(np.round(mt[i], 1)) for i in range(len(mt))])))
    return mt
