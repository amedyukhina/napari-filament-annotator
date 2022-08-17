import numpy as np
import pytest
from napari_filament_annotator.utils.postproc import snap_to_bright, gradient


@pytest.fixture
def grad(img_snake):
    return gradient(img_snake[0])


@pytest.fixture
def init_snake(img_snake):
    _, snake = img_snake
    init = snake.copy()
    init[1:-1] = init[1:-1] + (np.random.rand(*init[1:-1].shape) - 0.5) * np.array([2, 10, 10])
    return snake, init


def test_snapping(img_snake, init_snake, grad):
    img, _ = img_snake
    snake, init = init_snake
    snake2 = snap_to_bright(init, img=img, alpha=0.01, beta=0.1, gamma=1,
                            n_iter=100, end_coef=0, n_interp=0, remove_corners=False)
    snake3 = snap_to_bright(init, grad=grad, alpha=0.01, beta=0.1, gamma=1,
                            n_iter=100, end_coef=0, n_interp=0, remove_corners=False)
    assert len(snake) == len(snake2) == len(snake3)
    assert (snake[0] == snake2[0]).all()
    assert (snake[0] == snake3[0]).all()
    assert (snake[-1] == snake2[-1]).all()
    assert (snake[-1] == snake3[-1]).all()
    assert (snake2 == snake3).all()
    dist = np.mean(np.sqrt(np.sum((snake - snake2) ** 2, axis=1)))
    assert dist < 3


def test_snapping_interp(init_snake, grad):
    snake, init = init_snake
    snake2 = snap_to_bright(init, grad=grad, alpha=0.01, beta=0.1, gamma=1,
                            n_iter=100, end_coef=0, n_interp=5, remove_corners=True)
    assert len(snake2) == (len(snake) - 1) * 5 + 1
    assert (snake[0] == snake2[0]).all()
    assert (snake[-1] == snake2[-1]).all()
