"""This program shows `hyperfine` benchmark results as a box and whisker plot.

Quoting from the matplotlib documentation:
    The box extends from the lower to upper quartile values of the data, with
    a line at the median. The whiskers extend from the box to show the range
    of the data. Flier points are those past the end of the whiskers.
"""

import json
from typing_extensions import Annotated
from typing import Any
from pathlib import Path
import logging
from enum import Enum

import matplotlib.pyplot as plt
from matplotlib import rc
from typer import Typer, Option, Argument
from rich.logging import RichHandler
import seaborn as sns
import pandas as pd

DARK_BG = "#262626"

app = Typer()

FORMAT = "%(message)s"
logging.basicConfig(
    level=logging.INFO, format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)
log = logging.getLogger("plot-parameterised")


class ColourMode(Enum):
    dark = "dark"
    light = "light"


def parse_command(command: str) -> tuple[str, str]:
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


@app.command()
def main(
    file: Annotated[
        list[Path], Argument(default=..., help="JSON file(s) with benchmark results")
    ],
    title: str | None = Option(default=None, help="Plot Title"),
    output: list[Path] = Option(
        default=[], help="Save image to the given filename(s)."
    ),
    colour_mode: ColourMode = Option(
        default="light", help="Whether to use light or dark colour mode."
    ),
):
    rc("font", family="Geist")

    log.info("Loading results...")
    results: list[dict[str, Any]] = []
    for fname in file:
        with open(fname, encoding="utf-8") as f:
            results += list(json.load(f)["results"])

    log.info("Processing results...")

    data = pd.DataFrame(columns=["runtime", "perf-mode", "times"])

    for b in results:
        runtime, perf_mode = parse_command(b["command"])
        for time in b["times"]:
            data.loc[len(data)] = [runtime, perf_mode, time]

    log.info("Plotting...")

    sns.set_theme(font="Geist", style="whitegrid")

    if colour_mode == ColourMode.dark:
        plt.style.use("dark_background")

    grid = sns.FacetGrid(
        data, col="perf-mode", hue="runtime", sharey=True, sharex=True, height=8
    )
    grid.map(
        sns.boxplot,
        "runtime",
        "times",
        patch_artist=True,
        showfliers=False,
        gap=0.5,
    )

    if colour_mode == ColourMode.dark:
        grid.figure.set_facecolor(DARK_BG)
        for ax in grid.figure.axes:
            ax.set_facecolor(DARK_BG)

    if colour_mode == ColourMode.dark:
        plt.style.use("dark_background")

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


if __name__ == "__main__":
    app()
