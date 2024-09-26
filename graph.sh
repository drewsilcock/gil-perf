#!/bin/bash

set -euxo pipefail

run_names=(\
    '3-12-6' \
    '3-13-0rc2' \
    '3-13-0rc2t' \
    '3-13-0rc2t-g0' \
    '3-13-0rc2t-g1' \
)

python_versions=(\
    3.12.6 \
    3.13.0rc2 \
    3.13.0rc2t \
    3.13.0rc2t \
    3.13.0rc2t \
)

python_args=(\
    '' \
    '' \
    '' \
    '-X gil=0' \
    '-X gil=1' \
)

perf_script='mandelbrot'
perf_modes=('single' 'multi-threaded' 'multi-process')
parallel_perf_modes=('multi-threaded' 'multi-process')

perf_mode_shortnames=('s' 'mt' 'mp')
parallel_perf_mode_shortnames=('mt' 'mp')

input_dir='exports'
output_dir='exports'

function plot-whisker() {
    python scripts/plot_whisker.py \
        "$input_dir/bench-$perf_script.json" \
        --title "$1" \
        --output "$output_dir/bench-$perf_script.png"
}

function plot-parameterised() {
    python scripts/plot_parameterised.py \
        $input_dir/bench-cores-$perf_script-*.json \
        --title "$1" \
        --output "$output_dir/bench-cores-$perf_script-$1.png"
}

. .venv-3.12.6/bin/activate

plot-whisker 'GIL Performance Comparison'

#plot-parameterised multi-threaded 'GIL Performance – Mandelbrot N# Chunks (multi-threaded)'
#plot-parameterised multi-process 'GIL Performance – Mandelbrot N# Chunks (multi-process)'

