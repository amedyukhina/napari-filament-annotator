import numpy as np
from scipy import ndimage
from skimage.filters import sobel


def gradient(img, spacing=None):
    if spacing is None:
        spacing = np.ones(img.ndim)
    grad = [sobel(img, axis=i) / spacing[i] for i in range(img.ndim)]
    return grad


def interpolate(x, npoints=5):
    if npoints > 1:
        new_x = []
        for i in range(1, len(x)):
            new_x.append(np.linspace(x[i - 1], x[i], npoints, endpoint=False))
        new_x.append(x[-1:])
        new_x = np.concatenate(new_x, axis=0)
        return new_x
    else:
        return x


def remove_corners(x, k=3):
    d1, d2 = get_derivatives_1_2(x)
    d1 = np.sqrt((d1 ** 2).sum(1))
    d2 = np.sqrt((d2 ** 2).sum(1))
    d2 = np.where(d2 / d1 > 1, d2, 0)
    i1 = np.argmax(d2[:k])
    i2 = np.argmax(d2[-k:][::-1])
    x = x[i1:]
    if i2 > 0:
        x = x[:-i2]
    return x


def get_derivatives_1_2(x):
    x = np.concatenate([x[1:3][::-1], x, x[-3:-1][::-1]])
    d1 = x - np.roll(x, -1, 0)
    d2 = np.roll(x, 1, 0) + np.roll(x, -1, 0) - 2 * x
    return d1[2:-2], d2[2:-2]


def get_derivatives(x):
    x = np.concatenate([x[1:3][::-1], x, x[-3:-1][::-1]])
    d2 = np.roll(x, 1, 0) + np.roll(x, -1, 0) - 2 * x
    d4 = np.roll(x, 2, 0) - 4 * np.roll(x, 1, 0) + 6 * x - 4 * np.roll(x, -1, 0) + np.roll(x, -2, 0)
    return d2[2:-2], d4[2:-2]


def get_neighborhood_mask(img, snake, rad, sigma, start, end):
    img0 = img[tuple([slice(max(s, 0), e) for s, e in zip(start, end)])].astype(np.float32)
    imgf = np.zeros_like(img0)
    coords = np.int_(np.round_(snake - start))
    thr = np.median(img0[tuple(coords.transpose())]) * 3
    for coord in coords:
        cur_rad = rad if img0[tuple(coord)] < thr else [1, 3, 3]
        ind = tuple([slice(c - r, c + r + 1) for c, r in zip(coord, cur_rad)])
        imgf[ind] = img0[ind]
    imgf = ndimage.gaussian_filter(imgf, sigma=sigma)  # smooth the image
    return imgf


def evolve_snake(snake, n_iter, grad, spacing, alpha, beta, gamma, end_coef):
    coef = np.ones_like(snake)
    coef[0] = end_coef
    coef[-1] = end_coef
    c = np.arange(1, n_iter + 1)[::-1] / n_iter
    for it in range(n_iter):
        coord = tuple(np.int_(np.round_(snake)).transpose())
        fimg = np.array([grad[i][coord] for i in range(len(grad))])
        fimg = - fimg.transpose()
        fimg = fimg / fimg.max()

        d2, d4 = get_derivatives(snake * spacing)
        fsnake = d2 * alpha + d4 * beta
        fsnake = fsnake / np.max(fsnake)

        snake = snake - c[it] * coef * (fimg * gamma + fsnake) / (gamma + 1)
    return snake


def active_contour(snake, img=None, grad=None, spacing=None, alpha=0.01, beta=0.1, gamma=1, n_iter=1000, end_coef=0.01):
    if grad is None:
        if img is None:
            raise ValueError("Either image or gradient must be provided!")
        if spacing is None:
            spacing = np.ones(img.ndim)
        grad = gradient(img, spacing)

    snake = evolve_snake(snake, n_iter, grad, spacing, alpha, beta, gamma, end_coef)

    return snake
