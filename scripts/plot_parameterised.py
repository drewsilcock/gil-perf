"""This program shows parametrized `hyperfine` benchmark results as an
errorbar plot."""

import json
from pathlib import Path
import sys
from typing import Any
from typing_extensions import Annotated
import logging

import matplotlib.pyplot as plt
from typer import Typer, Option, Argument
from rich.logging import RichHandler

app = Typer()

FORMAT = "%(message)s"
logging.basicConfig(
    level=logging.WARNING, format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)
log = logging.getLogger("plot-parameterised")
log.root.setLevel(logging.INFO)
log.setLevel(logging.INFO)



def die(msg):
    log.error(f"fatal: {msg}")
    sys.exit(1)


def extract_parameters(results: list[dict[str, Any]]) -> tuple[str, list[float]]:
    """Return `(parameter_name: str, parameter_values: List[float])`."""
    if not results:
        die("no benchmark data to plot")

    (names, values) = zip(*(unique_parameter(b) for b in results))
    names = frozenset(names)
    if len(names) != 1:
        die(
            f"benchmarks must all have the same parameter name, but found: {sorted(names)}"
        )

    return (next(iter(names)), list(values))


def unique_parameter(benchmark: dict[str, Any]) -> tuple[str, float]:
    """Return the unique parameter `(name: str, value: float)`, or die."""
    params_dict = benchmark.get("parameters", {})

    if not params_dict:
        die("benchmarks must have exactly one parameter, but found none")

    if len(params_dict) > 1:
        die(
            f"benchmarks must have exactly one parameter, but found multiple: {sorted(params_dict)}"
        )

    [(name, value)] = params_dict.items()
    return (name, float(value))


@app.command()
def main(
    file: Annotated[
        list[Path], Argument(default=..., help="JSON file(s) with benchmark results")
    ],
    log_x: bool = Option(default=False, help="Use a logarithmic x (parameter) axis"),
    log_time: bool = Option(default=False, help="Use a logarithmic time axis"),
    title: str | None = Option(default=None, help="Title for plot"),
    labels: str | None = Option(
        default=None, help="Comma-separated list of labels for the plot legend"
    ),
    output: Path | None = Option(
        default=None, help="Save image to the given filename."
    ),
):
    labels_list = labels.split(",") if labels else None
    parameter_name: str | None = None

    log.info("Loading results...")
    for i, fname in enumerate(file):
        with open(fname) as f:
            results: list[dict[str, Any]] = list(json.load(f)["results"])

        (this_parameter_name, parameter_values) = extract_parameters(results)
        if parameter_name is not None and this_parameter_name != parameter_name:
            die(
                f"files must all have the same parameter name, but found {parameter_name!r} vs. {this_parameter_name!r}"
            )
        parameter_name = this_parameter_name

        times_mean = [b["mean"] for b in results]
        times_stddev = [b["stddev"] for b in results]

        plt.errorbar(
            x=parameter_values,
            y=times_mean,
            yerr=times_stddev,
            capsize=2,
            label=labels_list[i] if labels_list else fname,
        )

    parameter_name = parameter_name or "parameter"
    plt.xlabel(parameter_name)
    plt.ylabel("Time [s]")

    if log_time:
        plt.yscale("log")
    else:
        plt.ylim(0, None)

    if log_x:
        plt.xscale("log")

    if labels:
        plt.legend(labels_list)

    if title:
        plt.title(title)

    if output:
        log.info("Saving plot to %s...", output)
        plt.savefig(output)
    else:
        log.info("Rendering plot...")
        plt.show()

    log.info("Done")


if __name__ == "__main__":
    app()
