#!/bin/bash

set -euo pipefail

function info() {
    printf '\E[34m'; printf "[Info] "; printf '\E[0m'; echo "$@"
}


function plot-comparison() {
    info "Plotting comparison benchmarks"

    python -m gil_perf plot comparison \
        "$input_dir/bench-comparison.json" \
        --title "$1" \
        --colour-mode light \
        --output "$output_dir/bench-comparison-light.png" \
        --output "$output_dir/bench-comparison-light.svg"

    python -m gil_perf plot comparison \
        "$input_dir/bench-comparison.json" \
        --title "$1" \
        --colour-mode dark \
        --output "$output_dir/bench-comparison-dark.png" \
        --output "$output_dir/bench-comparison-dark.svg"
}

function plot-scaling() {
    info "Plotting scaling benchmarks"

    python -m gil_perf plot scaling \
        $input_dir/bench-scaling*.json \
        --title "$1" \
        --colour-mode light \
        --output "$output_dir/bench-scaling-light.png" \
        --output "$output_dir/bench-scaling-light.svg"

    python -m gil_perf plot scaling \
        $input_dir/bench-scaling*.json \
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

