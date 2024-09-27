from enum import Enum


class PerfScript(Enum):
    obrc = "obrc"
    mandelbrot = "mandelbrot"


class PerfMode(Enum):
    single = "single"
    multi_process = "multi-process"
    multi_threaded = "multi-threaded"


class ColourMode(Enum):
    dark = "dark"
    light = "light"
