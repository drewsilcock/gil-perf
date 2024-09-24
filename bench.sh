#!/bin/bash

set -euxo pipefail

function bench-script() {
    hyperfine \
        --warmup 2 \
        --export-json exports/bench-$1-$2.json \
        "source .venv-3.12.6/bin/activate && python -m gil_perf $1 $2" \
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
        "source .venv-3.12.6/bin/activate && python -m gil_perf $1 $2 --num-chunks {num_chunks}" \
        "source .venv-3.13.0rc2/bin/activate && python -m gil_perf $1 $2 --num-chunks {num_chunks}" \
        "source .venv-3.13.0rc2t/bin/activate && python -m gil_perf $1 $2 --num-chunks {num_chunks}" \
        "source .venv-3.13.0rc2t/bin/activate && python -X gil=0 -m gil_perf $1 $2 --num-chunks {num_chunks}" \
        "source .venv-3.13.0rc2t/bin/activate && python -X gil=1 -m gil_perf $1 $2 --num-chunks {num_chunks}"
}


mkdir -p exports

bench-script mandelbrot single
bench-script mandelbrot multi-threaded
bench-script mandelbrot multi-process

bench-script-cores mandelbrot multi-threaded
bench-script-cores mandelbrot multi-process
