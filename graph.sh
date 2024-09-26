#!/bin/bash

set -euo pipefail

function info() {
    printf '\E[34m'; printf "[Info] "; printf '\E[0m'; echo "$@"
}


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

function plot-comparison() {
    info "Plotting comparison benchmarks"

    python scripts/plot_whisker.py \
        "$input_dir/bench-comparison.json" \
        --title "$1" \
        --colour-mode light \
        --output "$output_dir/bench-comparison-light.png" \
        --output "$output_dir/bench-comparison-light.svg"

    python scripts/plot_whisker.py \
        "$input_dir/bench-comparison.json" \
        --title "$1" \
        --colour-mode dark \
        --output "$output_dir/bench-comparison-dark.png" \
        --output "$output_dir/bench-comparison-dark.svg"
}

function plot-scaling() {
    info "Plotting scaling benchmarks"

    python scripts/plot_parameterised.py \
        $input_dir/bench-scaling-*.json \
        --title "$1" \
        --colour-mode light \
        --output "$output_dir/bench-scaling-light.png" \
        --output "$output_dir/bench-scaling-light.svg"

    python scripts/plot_parameterised.py \
        $input_dir/bench-scaling-*.json \
        --title "$1" \
        --colour-mode dark \
        --output "$output_dir/bench-scaling-dark.png" \
        --output "$output_dir/bench-scaling-dark.svg"
}

. .venv-3.12.6/bin/activate

# If first argument is 'comparison', run 'plot-comparison', else if first arg is 'chunk-scan', run 'plot-chunk-scan', otherwise print help.
case $1 in
    comparison)
        title="${2:-GIL Performance Comparison}"
        input_dir="${3:-exports}"
        output_dir="$input_dir"

        plot-comparison "$title"
        ;;
    scaling)
        title="${2:-GIL Performance Scaling}"
        input_dir="${3:-exports}"
        output_dir="$input_dir"

        plot-scaling "$title"
        ;;
    *)
        echo "Usage: $0 {comparison|scaling} [title] [exports_dir]"
        exit 1
        ;;
esac

