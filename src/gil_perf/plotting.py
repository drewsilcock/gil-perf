from pathlib import Path
import json
from typing import Any

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

from .enums import ColourMode
from .logging import log

LIGHT_BG = "#f5f5f5"
LIGHT_AXES = "#383838"
LIGHT_TEXT = "#383838"
LIGHT_GRID = "#bfbfbf"

DARK_BG = "#262626"
DARK_AXES = "#cecece"
DARK_TEXT = "#cecece"
DARK_GRID = "#797979"


def _parse_command(command: str) -> tuple[str, str]:
    """
    Parse command and return the Python runtime, the Python GIL config and the profile mode.

    Examples:
        Input: ". .venv-3.13.0rc2t/bin/activate && python -X gil=1 -m gil_perf bench mandelbrot multi-process"
        Output: ("3.13.0rc2t-g1", "multi-process")

        Input: ". .venv-3.12.6/bin/activate && python  -m gil_perf bench mandelbrot single"
        Output: ("3.12.6", "single")

        Input: ". .venv-3.12.6/bin/activate && python  -m gil_perf bench mandelbrot multi-process --num-chunks 8"
        Output: ("3.12.6", "single")
    """
    parts = command.split(" ")
    runtime = parts[1].split("-")[1].split("/")[0]
    if "-X" in parts:
        runtime += "-g" + parts[parts.index("-X") + 1].split("=")[1]

    perf_mode = parts[parts.index("bench") + 2]
    return runtime, perf_mode


def _set_style(colour_mode: ColourMode) -> None:
    sns.set_theme(font="Geist", style="whitegrid", context="talk")

    if colour_mode == ColourMode.dark:
        plt.style.use("dark_background")

    bg_colour = DARK_BG if colour_mode == ColourMode.dark else LIGHT_BG
    grid_colour = DARK_GRID if colour_mode == ColourMode.dark else LIGHT_GRID
    axes_colour = DARK_AXES if colour_mode == ColourMode.dark else LIGHT_AXES
    text_colour = DARK_TEXT if colour_mode == ColourMode.dark else LIGHT_TEXT

    sns.set_style(
        rc={
            "figure.facecolor": bg_colour,
            "axes.facecolor": bg_colour,
            "axes.edgecolor": axes_colour,
            "grid.color": grid_colour,
            "text.color": text_colour,
        },
    )


def _use_dark_mode(grid: sns.FacetGrid) -> None:
    pass
    grid.figure.set_facecolor(DARK_BG)
    for ax in grid.figure.axes:
        ax.set_facecolor(DARK_BG)


def plot_mandelbrot(result: np.ndarray, output: Path | None) -> None:
    plt.imshow(result.T, interpolation="nearest")
    if output:
        plt.savefig(output)
    else:
        plt.show()


def plot_comparison(
    file: list[Path],
    title: str | None,
    output_dir: Path | None,
    colour_mode: ColourMode,
):
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

    _set_style(colour_mode)

    grid = sns.FacetGrid(
        data, col="perf_mode", hue="runtime", sharey=True, sharex=True, height=8
    )
    grid.map(
        sns.boxplot,
        "runtime",
        "time",
        order=sorted(data["runtime"].unique()),
        patch_artist=True,
        showfliers=False,
        gap=0,
        linewidth=1.5,
    )

    if title:
        grid.figure.subplots_adjust(top=0.9)
        grid.figure.suptitle(title)

    grid.set_axis_labels("Python Runtime", "Time (s)")
    grid.set(ylim=(0, None))
    grid.set_titles("Mode = {col_name}")

    if output_dir:
        output_path = output_dir / f"bench-comparison-{colour_mode.value}.png"

        log.info("Saving plot to %s...", output_path)
        if colour_mode == ColourMode.light:
            grid.figure.savefig(output_path)
        else:
            grid.figure.savefig(output_path, facecolor=DARK_BG)
    else:
        log.info("Rendering plot...")
        plt.show()

    log.info("Done")


def plot_scaling(
    file: list[Path],
    title: str | None,
    output: Path | None,
    colour_mode: ColourMode,
):
    data = pd.DataFrame(
        columns=["runtime", "perf_mode", "num_chunks", "time", "speedup"]
    )

    log.info("Loading results...")
    for i, fname in enumerate(file):
        with open(fname) as f:
            results: list[dict[str, Any]] = list(json.load(f)["results"])

        for b in results:
            runtime, perf_mode = _parse_command(b["command"])
            num_chunks = b["parameters"]["num_chunks"]

            for time in b["times"]:
                data.loc[len(data)] = [
                    runtime,
                    perf_mode,
                    num_chunks,
                    time,
                    np.float64(0),
                ]

    # Calculate speedup where each runtime and perf_mode is compared to the average
    # single-chunk time for that group.
    for i, row in data.iterrows():
        single_chunk_time = data[
            (data["runtime"] == row["runtime"])
            & (data["perf_mode"] == row["perf_mode"])
            & (data["num_chunks"] == "1")
        ]["time"].mean()

        data.loc[i, "speedup"] = single_chunk_time / row["time"]

    _set_style(colour_mode)
    sns.set_context("notebook")

    times_grid = sns.FacetGrid(
        data, col="perf_mode", hue="runtime", sharey=True, height=6
    )
    times_grid.map(sns.lineplot, "num_chunks", "time")

    speedup_grid = sns.FacetGrid(
        data, col="perf_mode", hue="runtime", sharey=True, height=6
    )
    speedup_grid.map(sns.lineplot, "num_chunks", "speedup")

    if title:
        times_grid.figure.subplots_adjust(top=0.9)
        times_grid.figure.suptitle(f"{title} – Time")

        speedup_grid.figure.subplots_adjust(top=0.9)
        speedup_grid.figure.suptitle(f"{title} – Speedup")

    times_grid.set_axis_labels("N# Threads / Processes", "Time (s)")
    times_grid.set(ylim=(0, None))
    times_grid.set_titles("Mode = {col_name}")
    times_grid.add_legend()

    speedup_grid.set_axis_labels("N# Threads / Processes", "Speedup")
    speedup_grid.set(ylim=(0, None))
    speedup_grid.set_titles("Mode = {col_name}")
    speedup_grid.add_legend()

    if output:
        time_path = output / f"bench-scaling-time-{colour_mode.value}.png"
        speedup_path = output / f"bench-scaling-speedup-{colour_mode.value}.png"

        log.info("Saving time plot to %s...", time_path)
        if colour_mode == ColourMode.light:
            times_grid.figure.savefig(time_path)
        else:
            _use_dark_mode(times_grid)
            times_grid.figure.savefig(time_path, facecolor=DARK_BG)

        log.info("Saving speedup plot to %s...", speedup_path)
        if colour_mode == ColourMode.light:
            speedup_grid.figure.savefig(speedup_path)
        else:
            _use_dark_mode(speedup_grid)
            speedup_grid.figure.savefig(speedup_path, facecolor=DARK_BG)
    else:
        log.info("Rendering plot...")
        plt.show()

    log.info("Done")
