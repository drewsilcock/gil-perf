import numpy as np
import matplotlib.pyplot as plt


def plot_mandelbrot(
    x_values: np.ndarray, y_values: np.ndarray, extent=tuple[float, float, float, float]
) -> None:
    plt.imshow([x_values, y_values], cmap="hot", interpolation="nearest")
    plt.show()
