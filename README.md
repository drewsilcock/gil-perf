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

To installed the necessary tools and Python versions:

```bash
./setup.sh
```

This may take a few minutes.

### Running the benchmarks

To run all the different benchmarks:

```bash
./bench.sh
```

### Generating performance graphs

The generate graphs from exported benchmarks:

```bash
./graph.sh
```
