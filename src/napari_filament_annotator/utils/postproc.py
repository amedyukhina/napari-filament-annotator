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


def active_contour(snake, img=None, spacing=None, sigma=0.1, rad=0.3,
                   alpha=0.01, beta=0.1, gamma=1, n_iter=1000, end_coef=0.01):
    start = np.int_(snake.min(0)) - rad
    end = np.int_(snake.max(0) + 1) + rad + 1
    imgf = get_neighborhood_mask(img, snake, rad, sigma, start, end)
    grad = gradient(imgf, spacing)

    c = np.arange(1, n_iter + 1)[::-1] / n_iter

    coef = np.ones_like(snake)
    coef[0] = end_coef
    coef[-1] = end_coef

    snake = snake - start

    for it in range(n_iter):
        coord = tuple(np.int_(np.round_(snake)).transpose())
        fimg = np.array([grad[i][coord] for i in range(len(grad))])
        fimg = - fimg.transpose()
        fimg = fimg / fimg.max()

        d2, d4 = get_derivatives(snake * spacing)
        fsnake = d2 * alpha + d4 * beta
        fsnake = fsnake / np.max(fsnake)

        # snake[1:-1] = snake[1:-1] - c[it] * (fimg[1:-1] * gamma + fsnake[1:-1]) / (gamma + 1)
        snake = snake - c[it] * coef * (fimg * gamma + fsnake) / (gamma + 1)
    return snake + start
