from multiprocessing import Process
from threading import Thread

from .common import split_chunks


MEASUREMENTS_FNAME = "measurements.txt"


class StationStats:
    def __init__(self, initial_temp: float) -> None:
        self.min = initial_temp
        self.max = initial_temp
        self.total = initial_temp
        self.count = 1


type Result = dict[str, StationStats]


def _load_lines() -> list[str]:
    with open(MEASUREMENTS_FNAME, "r") as fp:
        return fp.readlines()


def _parse_lines(lines: list[str], stations: Result) -> None:
    for line in lines:
        name, temp_str = line.split(";")
        temp = float(temp_str)

        if name not in stations:
            stations[name] = StationStats(temp)
        else:
            station = stations[name]
            station.min = min(station.min, temp)
            station.max = max(station.max, temp)
            station.total += temp
            station.count += 1


def _combine_results(results: list[Result]) -> Result:
    stations: Result = {}

    for result in results:
        for name, stats in result.items():
            if name not in stations:
                stations[name] = stats
            else:
                station = stations[name]
                station.min = min(station.min, stats.min)
                station.max = max(station.max, stats.max)
                station.total += stats.total
                station.count += stats.count

    return stations


def _stringify_result(result: Result) -> str:
    station_strs = [
        f"{name}={stats.min:.1f}/{stats.max:.1f}/{stats.total/stats.count:.1f}"
        for name, stats in result.items()
    ]
    station_strs.sort()

    return "{" + ", ".join(station_strs) + "}"


def obrc_single():
    lines = _load_lines()

    stations: Result = {}
    _parse_lines(lines, stations)

    print(_stringify_result(stations))


def obrc_multi_process(num_processes: int):
    results: list[Result] = []
    for _ in range(num_processes):
        results.append({})

    lines = _load_lines()
    chunks = split_chunks(lines, num_processes)

    processes: list[Process] = []
    for i in range(num_processes):
        process = Process(target=_parse_lines, args=(chunks[i], results[i]))
        process.start()
        processes.append(process)

    for process in processes:
        process.join()

    stations = _combine_results(results)
    print(_stringify_result(stations))

def obrc_multi_threaded(num_threads: int):
    results: list[Result] = []
    for _ in range(num_threads):
        results.append({})

    lines = _load_lines()
    chunks = split_chunks(lines, num_threads)

    threads: list[Thread] = []
    for i in range(num_threads):
        thread = Thread(target=_parse_lines, args=(chunks[i], results[i]))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    stations = _combine_results(results)
    print(_stringify_result(stations))

