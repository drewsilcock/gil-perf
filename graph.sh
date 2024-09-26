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

perf_modes=('single' 'multi-threaded' 'multi-process')
parallel_perf_modes=('multi-threaded' 'multi-process')

perf_mode_shortnames=('s' 'mt' 'mp')
parallel_perf_mode_shortnames=('mt' 'mp')

input_dir='exports'
output_dir='exports'

function plot-comparison() {
    python scripts/plot_whisker.py \
        "$input_dir/bench-comparison.json" \
        --title "GIL Performance Comparison" \
        --output "$output_dir/bench-comparison.png"
}

function plot-scaling() {
    python scripts/plot_parameterised.py \
        $input_dir/bench-scaling-*.json \
        --title "GIL Performance Scaling" \
        --output "$output_dir/bench-scaling.png"
}

. .venv-3.12.6/bin/activate

# If first argument is 'comparison', run 'plot-comparison', else if first arg is 'chunk-scan', run 'plot-chunk-scan', otherwise print help.
case $1 in
    comparison)
        plot-comparison 'GIL Performance Comparison'
        ;;
    scaling)
        plot-scaling 'GIL Performance Scaling'
        ;;
    *)
        echo "Usage: $0 {comparison|scaling}"
        exit 1
        ;;
esac

