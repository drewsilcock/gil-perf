#!/bin/bash

set -euxo pipefail

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

function warm-imports() {
    . .venv-$1/bin/activate
    python -c "import gil_perf"
    deactivate
}

function bench-script() {
    # Combine the Python versions and arguments into a single string containing multiple
    # commands, each within quotes.
    commands=()
    for i in "${!python_versions[@]}"; do
        for mode in "${perf_modes[@]}"; do
            local cmd=". .venv-${python_versions[$i]}/bin/activate && python ${python_args[$i]} -m gil_perf $perf_script $mode"
            commands+=("'$cmd'")
        done
    done
    
    eval hyperfine \
        --warmup 1 \
        --export-json exports/bench-$perf_script.json \
        "${commands[@]}"
}

function bench-script-cores() {
    commands=()
    for i in "${!python_versions[@]}"; do
        for mode in "${parallel_perf_modes[@]}"; do
            local cmd=". .venv-${python_versions[$i]}/bin/activate && python ${python_args[$i]} -m gil_perf $perf_script $mode"
            commands+=("'$cmd'")
        done
    done
    
    for i in "${!commands[@]}"; do
        cmd="${commands[$i]}"
        name="${run_names[$i]}"
        
        eval hyperfine \
            --warmup 1 \
            --runs 4 \
            --parameter-scan num_chunks 1 24 \
            --export-json exports/bench-cores-$perf_script-$1-$name.json \
            "$cmd"
    done
}

# Benchmarking takes ages to run, don't want to get rid of or overwrite old results.
if [ -d exports ]; then
    current_time=$(date "+%Y-%m-%d-%H-%M-%S")
    mv exports "exports-$current_time"
fi

mkdir -p exports

for python_version in "${python_versions[@]}"; do
    warm-imports $python_version
done

# Runs 5x3 = 15 benchmarks and outputs to a single file to be used by the whisker
# plotter.
bench-script

# Runs 5x32 = 160 benchmarks and outputs to a separate file for each run.
bench-script-cores multi-threaded

# Runs another 5x32 = 160 benchmarks and outputs to a separate file for each run.
bench-script-cores multi-process

# Total n# benchmarks = 15 + 160 + 160 = 335
# Single-threaded takes ~10 seconds, multi-threaded/process takes ~3 seconds so total
# time is between 16 minutes and 55 minutes. In truth, 32-threaded GIL-enabled Python
# takes much longer.
