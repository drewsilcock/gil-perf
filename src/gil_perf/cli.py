from os import cpu_count
from pathlib import Path
from typing_extensions import Annotated

from typer import Typer, Option, Argument

from .obrc import obrc_single, obrc_multi_process, obrc_multi_threaded
from .mandelbrot import (
    mandelbrot_single,
    mandelbrot_multi_process,
    mandelbrot_multi_threaded,
)
from .enums import PerfMode, PerfScript, ColourMode
from .plotting import plot_comparison, plot_scaling

app = Typer()
plot_app = Typer(name="plot")
app.add_typer(plot_app)


@app.command()
def bench(
    script: PerfScript = Argument(
        default=..., help="Which performance assessment script to run."
    ),
    mode: PerfMode = Argument(
        default=...,
        help="Whether to use single-threaded, multi-process or multi-threaded modes for performance assessment.",
    ),
    num_chunks: int | None = Option(
        default=None,
        help="integer number of processes / threads – defaults to number of CPUs (optional)",
    ),
):
    if num_chunks is None:
        num_chunks = cpu_count() or 8

    match script:
        case PerfScript.obrc:
            match mode:
                case PerfMode.single:
                    obrc_single()
                case PerfMode.multi_process:
                    obrc_multi_process(num_chunks)
                case PerfMode.multi_threaded:
                    obrc_multi_threaded(num_chunks)
        case PerfScript.mandelbrot:
            match mode:
                case PerfMode.single:
                    mandelbrot_single()
                case PerfMode.multi_process:
                    mandelbrot_multi_process(num_chunks)
                case PerfMode.multi_threaded:
                    mandelbrot_multi_threaded(num_chunks)


@plot_app.command()
def comparison(
    file: Annotated[
        list[Path], Argument(default=..., help="JSON file(s) with benchmark results")
    ],
    title: str | None = Option(default=None, help="Title for plot."),
    output_dir: Path | None = Option(
        default=None,
        help="Save images to this directory. If not specified, images will be displayed instead of saved to disk.",
    ),
):
    plot_comparison(file, title, output_dir, ColourMode.light)
    plot_comparison(file, title, output_dir, ColourMode.dark)


@plot_app.command()
def scaling(
    file: Annotated[
        list[Path], Argument(default=..., help="JSON file(s) with benchmark results")
    ],
    title: str | None = Option(default=None, help="Title for plot."),
    output_dir: Path | None = Option(
        default=None,
        help="Save images to this directory. If not specified, images will be displayed instead of saved to disk.",
    ),
):
    plot_scaling(file, title, output_dir, ColourMode.light)
    plot_scaling(file, title, output_dir, ColourMode.dark)
