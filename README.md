# GIL Performance Testing

This repository contains some code to test the performance of Python with experimental support for free-threading enabled and disabled, for comparison.

## Getting started

### Installing prerequisites

First, you need to install the various Python versions using pyenv (rye and uv don't have the unreleased release candidates for v3.13 yet).

There are a few external dependencies for Pillow. If you're on Ubuntu, you can install via:

```bash
sudo apt update
sudo apt install libjpeg8-dev zlib1g-dev libtiff-dev libfreetype6 libfreetype6-dev libwebp-dev libopenjp2-7-dev libopenjp2-7-dev -y
```

You also need to install hyperfine as per [github.com/sharkdp/hyperfine](https://github.com/sharkdp/hyperfine?tab=readme-ov-file#installation).

To installed the necessary tools and Python versions:

```bash
./setup.sh
```

This may take a few minutes.

### Running the benchmarks

There are two different benchmarks to run, "comparison" which compares the execution time of the various runtimes and performance modes, and "scaling" which compares how the overall execution times changes as you increase the number of threads / processes. To run them:

```bash
./bench.sh comparison
./bench.sh scaling
```

### Generating performance graphs

The generate graphs from exported benchmarks:

```bash
./graph.sh comparison
./graph.sh scaling
```
