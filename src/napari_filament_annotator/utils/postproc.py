import numpy as np
from skimage.filters import sobel


def gradient(img, spacing=None):
    """
    Calculate image gradient along all axes.

    Parameters
    ----------
    img : np.ndarray
        Input 3D image
    spacing : tuple, list or array
        Voxel size, (z, y, x).

    Returns
    -------
    list of np.ndarray:
        Image gradients along all three axes.
        List of length 3, each element having the same shape as the input image.
    """
    if spacing is None:
        spacing = np.ones(img.ndim)
    grad = [sobel(img, axis=i) / spacing[i] for i in range(img.ndim)]
    return grad


def snap_to_bright(snake, img=None, grad=None, spacing=None,
                   alpha=0.01, beta=0.1, gamma=1,
                   n_iter=1000, end_coef=0.01, n_interp=5, **_):
    """
    Snap the annotation to the brightest intensity and regularize the curve based on active contours.

    Parameters
    ----------
    snake : np.ndarray
        N x 3 array of the filament coordinates.
    img : np.ndarray
        3D input image (after smoothing, if applicable)
    grad : list of np.ndarray
        Image gradients along all three axes.
        List of length 3, each element having the same shape as the input image.
    spacing : tuple, list or array
        Voxel size, (z, y, x).
    alpha : float
        Active contour weight for the first derivative.
    beta : float
        Active contour weight for the seconf derivative.
    gamma : float
        Active contour weight for the image contribution.
    n_iter : int
        Number of iterations of the active contour.
        Width of the annotation lines in the viewer.
    end_coef : float
        Coefficient (between 0 and 1) to scale the forces applied to the contour end points.
        Set to 0 to fix the end points.
    n_interp : int
        Number of points to interpolate between each annotated point.

    Returns
    -------
    np.ndarray
        M x 3 array of regularized filament coordinates.
        M is approximately equal to N * n_interp

    """
    if spacing is None:
        spacing = np.ones(3)
    if grad is None:
        if img is None:
            raise ValueError("Either image or gradient must be provided!")
        grad = gradient(img, spacing)

    if not isinstance(snake, np.ndarray) or len(snake.shape) != 2 or snake.shape[1] != 3:
        raise ValueError("Input snake must be a numpy array of shape N x 3")

    snake = _interpolate(snake, npoints=n_interp)  # interpolate between the points
    snake = _evolve_snake(snake, n_iter, grad, spacing, alpha, beta, gamma, end_coef)  # evolve the snake

    return snake


def _evolve_snake(snake, n_iter, grad, spacing, alpha, beta, gamma, end_coef):
    coef = np.ones_like(snake)  # coefficient to weight end points vs all other points
    coef[0] = end_coef
    coef[-1] = end_coef
    c = np.arange(1, n_iter + 1)[::-1] / n_iter  # weight for each iteration; linearly decrease with each iteration
    for it in range(n_iter):
        coord = tuple(np.int_(np.round_(snake)).transpose())

        # normalize image force, based on the gradient at the current coordinate
        fimg = np.array([grad[i][coord] for i in range(len(grad))])
        fimg = - fimg.transpose()
        fimg = fimg / fimg.max()

        # normalized snake (internal) force
        d2, d4 = _get_derivatives_2_4(snake * spacing)
        fsnake = d2 * alpha + d4 * beta
        fsnake = fsnake / np.max(fsnake)

        # update the snake with the final force
        snake = snake - c[it] * coef * (fimg * gamma + fsnake) / (gamma + 1)
        # make sure snake coordinates are not outside image
        snake = _fit_to_image_shape(snake, grad[0].shape)
    return snake


def _fit_to_image_shape(snake, shape):
    shape = np.array(shape) - 1
    snake = np.array([np.max([[0, 0, 0], np.min([shape, snake[i]], axis=0)], axis=0) for i in range(len(snake))])
    return snake


def _interpolate(x, npoints=5):
    if npoints > 1:
        new_x = []
        for i in range(1, len(x)):
            new_x.append(np.linspace(x[i - 1], x[i], npoints, endpoint=False))
        new_x.append(x[-1:])
        new_x = np.concatenate(new_x, axis=0)
        return new_x
    else:
        return x


def _remove_corners(x, k=3):
    # first and second derivatives
    d1, d2 = _get_derivatives_1_2(x)
    d1 = np.sqrt((d1 ** 2).sum(1))
    d2 = np.sqrt((d2 ** 2).sum(1))

    # only consider points where the second derivative is greater than the first
    d2 = np.where(d2 / d1 > 1, d2, 0)

    # find the maximum of the second derivative (the corners) among the first and the last k points
    i1 = np.argmax(d2[:k])
    i2 = np.argmax(d2[-k:][::-1])

    # remove points before and after these maxima
    x = x[i1:]
    if i2 > 0:
        x = x[:-i2]
    return x


def _get_derivatives_1_2(x):
    x = np.concatenate([x[1:3][::-1], x, x[-3:-1][::-1]])
    d1 = x - np.roll(x, -1, 0)
    d2 = np.roll(x, 1, 0) + np.roll(x, -1, 0) - 2 * x
    return d1[2:-2], d2[2:-2]


def _get_derivatives_2_4(x):
    x = np.concatenate([x[1:3][::-1], x, x[-3:-1][::-1]])
    d2 = np.roll(x, 1, 0) + np.roll(x, -1, 0) - 2 * x
    d4 = np.roll(x, 2, 0) - 4 * np.roll(x, 1, 0) + 6 * x - 4 * np.roll(x, -1, 0) + np.roll(x, -2, 0)
    return d2[2:-2], d4[2:-2]
