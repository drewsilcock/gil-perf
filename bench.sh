#!/bin/bash

set -euo pipefail

function info() {
    printf '\E[34m'; printf "[Info] "; printf '\E[0m'; echo "$@"
}

run_names=(\
    '3-12-6' \
    '3-13-0rc2' \
    '3-13-0rc2t' \
    '3-13-0rc2t-g1' \
)

python_versions=(\
    3.12.6 \
    3.13.0rc2 \
    3.13.0rc2t \
    3.13.0rc2t \
)

python_args=(\
    '' \
    '' \
    '' \
    '-X gil=1' \
)

perf_script='mandelbrot'
perf_modes=('single' 'multi-threaded' 'multi-process')
parallel_perf_modes=('multi-threaded' 'multi-process')

output_dir='exports'

function warm-imports() {
    . .venv-$1/bin/activate
    python -c "import gil_perf"
    deactivate
}

# Runs 4x3 = 12 benchmarks with 10 runs and 1 warmup = 121 executions.
function bench-comparison() {
    commands=()
    for i in "${!python_versions[@]}"; do
        for mode in "${perf_modes[@]}"; do
            local cmd=". .venv-${python_versions[$i]}/bin/activate && python ${python_args[$i]} -m gil_perf $perf_script $mode"
            commands+=("'$cmd'")
        done
    done

    info "Running ${#commands[@]} comparison benchmarks"

    output_fname="$output_dir/bench-comparison.json"

    # Eval is needed to combine the Python versions and arguments into a single string
    # containing multiple commands, each within quotes.
    eval hyperfine \
        --warmup 1 \
        --export-json "$output_fname" \
        "${commands[@]}"

    info "Exported results to $output_fname"
}

# Runs 4x2 = 8 benchmarks with 1-24 parameter scan and 1 warmup per benchmark = 200 executions.
function bench-scaling() {
    commands=()
    names=()
    for i in "${!python_versions[@]}"; do
        for mode in "${parallel_perf_modes[@]}"; do
            local cmd=". .venv-${python_versions[$i]}/bin/activate && python ${python_args[$i]} -m gil_perf $perf_script $mode --num-chunks {num_chunks}"
            commands+=("'$cmd'")
            names+=("${run_names[$i]}-$mode")
        done
    done

    info "Running ${#commands[@]} scaling benchmarks"
    
    output_fname="$output_dir/bench-scaling.json"

    eval hyperfine \
        --warmup 1 \
        --runs 4 \
        --parameter-scan num_chunks 1 24 \
        --export-json $output_fname \
        "${commands[@]}"

    info "Exported results to $output_fname"
}

# Benchmarking takes ages to run, don't want to get rid of or overwrite old results.
if [ -d exports ]; then
    current_time=$(date "+%Y-%m-%dT%H-%M-%S")

    info "Safely moving old exports to exports-$current_time"
    mv exports "exports-$current_time"
fi

mkdir -p exports

info "Warming up imports"
for python_version in "${python_versions[@]}"; do
    warm-imports $python_version
done

# If first argument is 'comparison', run the comparison benchmarks. If first argument is
# 'chunk-scan', run the chunk scan benchmarks. Otherwise, show help message.
case $1 in
    comparison)
        bench-comparison
        ;;
    scaling)
        bench-scaling
        ;;
    *)
        echo "Usage: $0 {comparison|scaling}"
        exit 1
        ;;
esac

info "Done"
