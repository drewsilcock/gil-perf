import numpy as np
import matplotlib.pyplot as plt


def plot_mandelbrot(result: np.ndarray) -> None:
    plt.imshow(result.T, interpolation="nearest")
    plt.show()
