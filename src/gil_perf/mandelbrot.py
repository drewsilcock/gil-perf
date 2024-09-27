from multiprocessing import Process, Array
from multiprocessing.sharedctypes import SynchronizedArray
from threading import Thread

import numpy as np

from .common import chunk_indices


MAX_ITER = 1000
MIN_X, MAX_X = -2.0, 1.0
MIN_Y, MAX_Y = -1.5, 1.5
DENSITY = 1000


def _generate_grid() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    x_values = np.linspace(MIN_X, MAX_X, DENSITY)
    y_values = np.linspace(MIN_Y, MAX_Y, DENSITY)
    result = np.empty((len(x_values), len(y_values)))

    return x_values, y_values, result


def _check_convergence(x: float, y: float) -> int:
    c = complex(x, y)
    z = 0

    for i in range(MAX_ITER):
        z = z * z + c
        if abs(z) > 2:
            return i

    return MAX_ITER


def _converge_chunk(
    x_values: np.ndarray,
    y_values: np.ndarray,
    x_indices: tuple[int, int],
    y_indices: tuple[int, int],
    result: np.ndarray,
):
    for i in range(x_indices[0], x_indices[1]):
        x = x_values[i]
        for j in range(y_indices[0], y_indices[1]):
            y = y_values[j]
            result[i, j] = _check_convergence(x, y)


def _converge_shared_chunk(
        x_values: np.ndarray,
    y_values: np.ndarray,
    x_indices: tuple[int, int],
    y_indices: tuple[int, int],
    result: SynchronizedArray,
):
    np_result = np.frombuffer(result.get_obj())
    np_result = np_result.reshape((len(x_values), len(y_values)))
    _converge_chunk(x_values, y_values, x_indices, y_indices, np_result)


def mandelbrot_single():
    x_values, y_values, result = _generate_grid()
    _converge_chunk(x_values, y_values, (0, len(x_values)), (0, len(y_values)), result)


def mandelbrot_multi_process(num_processes: int):
    x_values, y_values, _ = _generate_grid()
    result = Array("d", len(x_values) * len(y_values))

    # Just chunk the x values, there's no point splitting into a grid or anything.
    x_chunk_indices = chunk_indices(len(x_values), num_processes)

    processes: list[Process] = []
    for i in range(num_processes):
        process = Process(
            target=_converge_shared_chunk,
            args=(
                x_values,
                y_values,
                x_chunk_indices[i],
                (0, len(y_values)),
                result,
            ),
        )
        process.start()
        processes.append(process)

    for process in processes:
        process.join()

    np_result = np.frombuffer(result.get_obj())
    np_result = np_result.reshape((len(x_values), len(y_values)))


def mandelbrot_multi_threaded(num_threads: int):
    print("Using %d threads", num_threads)
    x_values, y_values, result = _generate_grid()

    # Just chunk the x values, there's no point splitting into a grid or anything.
    x_chunk_indices = chunk_indices(len(x_values), num_threads)

    threads: list[Thread] = []
    for i in range(num_threads):
        thread = Thread(
            target=_converge_chunk,
            args=(x_values, y_values, x_chunk_indices[i], (0, len(y_values)), result),
        )
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()
