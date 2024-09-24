# GIL Performance Testing

This repository contains some code to test the performance of Python with experimental support for free-threading enabled and disabled, for comparison.

## Getting started

### Installing prerequisites

First, you need to install the various Python versions using pyenv (rye and uv don't have the unreleased release candidates for v3.13 yet).

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
