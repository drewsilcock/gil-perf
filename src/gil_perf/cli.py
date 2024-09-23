from enum import Enum
from os import cpu_count

from typer import Typer, Option, Argument

from .obrc import obrc_single, obrc_multi_process, obrc_multi_threaded
from .mandelbrot import (
    mandelbrot_single,
    mandelbrot_multi_process,
    mandelbrot_multi_threaded,
)

app = Typer()


class PerfScript(Enum):
    obrc = "obrc"
    mandelbrot = "mandelbrot"


class PerfMode(Enum):
    single = "single"
    multi_process = "multi-process"
    multi_threaded = "multi-threaded"


@app.command()
def obrc(
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
        case "obrc":
            match mode:
                case "single":
                    obrc_single()
                case "multi-process":
                    obrc_multi_process(num_chunks)
                case "multi-threaded":
                    obrc_multi_threaded(num_chunks)
        case "mandelbrot":
            match mode:
                case "single":
                    mandelbrot_single()
                case "multi-process":
                    mandelbrot_multi_process(num_chunks)
                case "multi-threaded":
                    mandelbrot_multi_threaded(num_chunks)
