from pathlib import Path
import json
from typing import Any

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc
import seaborn as sns
import pandas as pd

from .enums import ColourMode
from .logging import log

DARK_BG = "#262626"


def _parse_command(command: str) -> tuple[str, str]:
    """
    Parse command and return the Python runtime, the Python GIL config and the profile mode.

    Examples:
        Input: ". .venv-3.13.0rc2t/bin/activate && python -X gil=1 -m gil_perf mandelbrot multi-process"
        Output: ("3.13.0rc2t-g1", "multi-process")

        Input: ". .venv-3.12.6/bin/activate && python  -m gil_perf mandelbrot single"
        Output: ("3.12.6", "single")
    """
    parts = command.split(" ")
    runtime = parts[1].split("-")[1].split("/")[0]
    if "-X" in parts:
        runtime += "-g" + parts[parts.index("-X") + 1].split("=")[1]

    perf_mode = parts[-1]
    return runtime, perf_mode


def plot_mandelbrot(result: np.ndarray, output: Path | None) -> None:
    plt.imshow(result.T, interpolation="nearest")
    if output:
        plt.savefig(output)
    else:
        plt.show()


def plot_whiskers(
    file: list[Path],
    title: str | None,
    output: list[Path],
    colour_mode: ColourMode,
):
    rc("font", family="Geist")

    log.info("Loading results...")
    results: list[dict[str, Any]] = []
    for fname in file:
        with open(fname, encoding="utf-8") as f:
            results += list(json.load(f)["results"])

    log.info("Processing results...")

    data = pd.DataFrame(columns=["runtime", "perf_mode", "time"])

    for b in results:
        runtime, perf_mode = _parse_command(b["command"])
        for time in b["times"]:
            data.loc[len(data)] = [runtime, perf_mode, time]

    log.info("Plotting...")

    sns.set_theme(font="Geist", style="whitegrid")

    if colour_mode == ColourMode.dark:
        plt.style.use("dark_background")

    grid = sns.FacetGrid(
        data, col="perf_mode", hue="runtime", sharey=True, sharex=True, height=8
    )
    grid.map(
        sns.boxplot,
        "runtime",
        "time",
        patch_artist=True,
        showfliers=False,
        gap=0.5,
    )

    if colour_mode == ColourMode.dark:
        plt.style.use("dark_background")
        grid.figure.set_facecolor(DARK_BG)
        for ax in grid.figure.axes:
            ax.set_facecolor(DARK_BG)

    if title:
        grid.figure.subplots_adjust(top=0.9)
        grid.figure.suptitle(title)

    grid.set_axis_labels("Python Runtime", "Time (s)")
    grid.set(ylim=(0, None))
    grid.set_titles("Mode = {col_name}")

    if output:
        for fname in output:
            log.info("Saving plot to %s...", fname)
            if colour_mode == ColourMode.dark:
                grid.figure.savefig(fname, facecolor=DARK_BG)
            else:
                grid.figure.savefig(fname)
    else:
        log.info("Rendering plot...")
        plt.show()

    log.info("Done")


def plot_parameterised(
    file: list[Path],
    title: str | None,
    output: list[Path],
    colour_mode: ColourMode,
):
    mean_times = pd.DataFrame(
        columns=["runtime", "perf_mode", "num_chunks", "mean_time"]
    )
    all_times = pd.DataFrame(columns=["runtime", "perf_mode", "num_chunks", "time"])

    log.info("Loading results...")
    for i, fname in enumerate(file):
        with open(fname) as f:
            results: list[dict[str, Any]] = list(json.load(f)["results"])

        for b in results:
            runtime, perf_mode = _parse_command(b["command"])
            num_chunks = b["parameters"]["num_chunks"]

            mean_times.loc[len(mean_times)] = [
                runtime,
                perf_mode,
                num_chunks,
                b["mean"],
            ]

            for time in b["times"]:
                all_times.loc[len(all_times)] = [runtime, perf_mode, num_chunks, time]

    sns.set_theme(font="Geist", style="whitegrid")

    if colour_mode == ColourMode.dark:
        plt.style.use("dark_background")

    grid = sns.FacetGrid(
        all_times, col="perf_mode", hue="runtime", sharey=True, sharex=True, height=8
    )
    grid.map(sns.lineplot, "num_chunks", "time")

    if colour_mode == ColourMode.dark:
        plt.style.use("dark_background")
        grid.figure.set_facecolor(DARK_BG)
        for ax in grid.figure.axes:
            ax.set_facecolor(DARK_BG)

    if title:
        grid.figure.subplots_adjust(top=0.9)
        grid.figure.suptitle(title)

    grid.set_axis_labels("N# Threads / Processes", "Time (s)")
    grid.set(ylim=(0, None))
    grid.set_titles("Mode = {col_name}")
    grid.add_legend()

    if output:
        for fname in output:
            log.info("Saving plot to %s...", fname)
            if colour_mode == ColourMode.dark:
                grid.figure.savefig(fname, facecolor=DARK_BG)
            else:
                grid.figure.savefig(fname)
    else:
        log.info("Rendering plot...")
        plt.show()

    log.info("Done")
