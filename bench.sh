#!/bin/bash

set -euxo pipefail

function warm-imports() {
    source .venv-$1/bin/activate
    python -c "import gil_perf"
    deactivate
}

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

python_versions=(3.12.6 3.13.0rc2 3.13.0rc2t)

mkdir -p exports

for python_version in "${python_versions[@]}"; do
    warm-imports $python_version
done

bench-script mandelbrot single
bench-script mandelbrot multi-threaded
bench-script mandelbrot multi-process

bench-script-cores mandelbrot multi-threaded
bench-script-cores mandelbrot multi-process
