import os
import shutil
import tempfile

import numpy as np
import pytest
from scipy import ndimage


@pytest.fixture(scope='module')
def polygons():
    return [[[([0., 73., 12.]),
              ([0., 73., 25.]),
              ([0., 73., 38.]),
              ([0., 73., 55.]),
              ([0., 73., 69.])],
             [([10., 85., 12.]),
              ([10., 85., 25]),
              ([10., 85., 38]),
              ([10., 85., 55.]),
              ([10., 85., 69.])]],
            [[([0., 85., 15.]),
              ([0., 85., 29.]),
              ([0., 85., 41.]),
              ([0., 85., 54.]),
              ([0., 85., 61.]),
              ([0., 85., 72.])],
             [([10., 73., 15.]),
              ([10., 73., 29.]),
              ([10., 73., 41.]),
              ([10., 73., 54.]),
              ([10., 73., 61.]),
              ([10., 73., 72.])]]]


@pytest.fixture(scope='module')
def tetragons(polygons):
    npt1 = polygons[0][0]
    npt2 = polygons[1][0]
    fpt1 = polygons[0][1]
    fpt2 = polygons[1][1]

    p1 = [npt1[0], npt1[1], fpt1[1], fpt1[1]]
    p2 = [npt2[0], npt2[1], fpt2[1], fpt2[0]]
    return p1, p2


@pytest.fixture(scope='module')
def paths():
    n = np.random.randint(5, 10)
    paths = []
    for i in range(n):
        l = np.random.randint(10, 15)
        path = np.random.randint(0, 100, (l, 3))
        paths.append(path)
    return paths


@pytest.fixture(scope='module')
def img_snake():
    n = 100
    n2 = 50
    img = np.zeros((10, 50, 50))
    z = np.int_(np.round_(np.linspace(2, 8, n)))
    y = np.int_(np.round_(np.linspace(10, 30, n)))
    x = np.int_(np.round_(np.linspace(5, 40, n) + 10 * np.sin(np.linspace(0, 5, n))))
    img[z, y, x] = 1

    img = ndimage.gaussian_filter(img, 2)

    z2 = np.int_(np.round_(np.linspace(2, 8, n2)))
    y2 = np.int_(np.round_(np.linspace(10, 30, n2)))
    x2 = np.int_(np.round_(np.linspace(5, 40, n2) + 10 * np.sin(np.linspace(0, 5, n2))))
    return img, np.array([z2, y2, x2]).transpose()


@pytest.fixture(scope='module')
def tmp_path():
    path = tempfile.mkdtemp()
    os.makedirs(path, exist_ok=True)
    yield path
    shutil.rmtree(path)
