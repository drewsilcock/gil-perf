#!/bin/bash

set -euxo pipefail

function plot-whisker() {
    python scripts/plot_whisker.py \
        exports/bench-$1-$2.json \
        --title "$3" \
        --output "exports/bench-$1-$2.png" \
        --labels '3.12,3.13,3.13 (ft GIL auto),3.13 (ft GIL disabled),3.13 (ft GIL enabled)'
}

function plot-parameterised() {
    python scripts/plot_parameterised.py \
        exports/bench-cores-$1-$2.json \
        --title "$3" \
        --output "exports/bench-cores-$1-$2.png"
}

. .venv-3.12.6/bin/activate

plot-whisker mandelbrot single 'GIL Performance – Mandelbrot (single-threaded)'
plot-whisker mandelbrot multi-threaded 'GIL Performance – Mandelbrot (multi-threaded)'
plot-whisker mandelbrot multi-process 'GIL Performance – Mandelbrot (multi-process)'

plot-parameterised mandelbrot multi-threaded 'GIL Performance – Mandelbrot N# Chunks (multi-threaded)'
plot-parameterised mandelbrot multi-process 'GIL Performance – Mandelbrot N# Chunks (multi-process)'
