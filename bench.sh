#!/bin/bash

set -euxo pipefail

function setup-venv() {
    export PYTHON_VERSION=$1
    python -m venv .venv-$PYTHON_VERSION
    source .venv-$PYTHON_VERSION/bin/activate
    poetry install
}

function bench-script() {
    hyperfine \
        --warmup 2 \
        --export-json exports/bench-$1-$2.json \
        "source .venv-2.12.6/bin/activate && python -m gil_perf $1 $2" \
        "source .venv-3.13.0rc2/bin/activate && python -m gil_perf $1 $2" \
        "source .venv-3.13.0rc2t/bin/activate && python -m gil_perf $1 $2" \
        "source .venv-3.13.0rc2t/bin/activate && python -X gil=0 -m gil_perf $1 $2" \
        "source .venv-3.13.0rc2t/bin/activate && python -X gil=1 -m gil_perf $1 $2"
}

function bench-script-cores() {
    hyperfine \
        --warmup 2 \
        --parameter-scan num_chunks 1 32 \
        --export-json exports/bench-cores-$1-$2.json \
        "source .venv-2.12.6/bin/activate && python -m gil_perf $1 $2 {num_chunks}" \
        "source .venv-3.13.0rc2/bin/activate && python -m gil_perf $1 $2 {num_chunks}" \
        "source .venv-3.13.0rc2t/bin/activate && python -m gil_perf $1 $2 {num_chunks}" \
        "source .venv-3.13.0rc2t/bin/activate && python -X gil=0 -m gil_perf $1 $2 {num_chunks}" \
        "source .venv-3.13.0rc2t/bin/activate && python -X gil=1 -m gil_perf $1 $2 {num_chunks}"
}


python_versions=(3.12.6 3.13.0rc2 3.13.0rc2t)

for python_version in "${python_versions[@]}"; do
    setup-venv $python_version
done

mkdir -p exports

bench-script mandelbrot single
bench-script mandelbrot multi-threaded
bench-script mandelbrot multi-process

bench-script-cores mandelbrot multi-threaded
bench-script-cores mandelbrot multi-process
