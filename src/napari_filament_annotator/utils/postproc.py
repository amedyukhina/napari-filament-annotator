import numpy as np
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


def get_derivatives(x):
    x = np.concatenate([x[:1], x[:1], x, x[-1:], x[-1:]])
    d2 = np.roll(x, 1, 0) + np.roll(x, -1, 0) - 2 * x
    d4 = np.roll(x, 2, 0) - 4 * np.roll(x, 1, 0) + 6 * x - 4 * np.roll(x, -1, 0) + np.roll(x, -2, 0)
    return d2[2:-2], d4[2:-2]


def active_contour(snake, img=None, grad=None, spacing=None, alpha=0.01, beta=0.1, gamma=1, n_iter=1000):
    if grad is None:
        if img is None:
            raise ValueError("Either image or gradient must be provided!")
        if spacing is None:
            spacing = np.ones(img.ndim)
        grad = gradient(img, spacing)

    c = np.arange(1, n_iter + 1)[::-1] / n_iter

    for it in range(n_iter):
        coord = tuple(np.int_(np.round_(snake)).transpose())
        fimg = np.array([grad[i][coord] for i in range(len(grad))])
        fimg = - fimg.transpose()
        fimg = fimg / fimg.max()

        d2, d4 = get_derivatives(snake * spacing)
        fsnake = d2 * alpha + d4 * beta
        fsnake = fsnake / np.max(fsnake)

        snake[1:-1] = snake[1:-1] - c[it] * (fimg[1:-1] * gamma + fsnake[1:-1]) / (gamma + 1)
    return snake
