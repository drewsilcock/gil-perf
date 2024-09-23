from typing import TypeVar

T = TypeVar("T")


def split_chunks(values: list[T], num_chunks: int) -> list[list[T]]:
    chunk_size = len(values) // num_chunks
    chunks = [values[i * chunk_size : (i + 1) * chunk_size] for i in range(num_chunks)]

    # Extend last chunk to include remainder.
    if len(values) % num_chunks:
        chunks[-1].extend(values[num_chunks * chunk_size :])

    return chunks


def chunk_indices(num_values: int, num_chunks: int) -> list[tuple[int, int]]:
    chunk_size = num_values // num_chunks
    chunks = [(i * chunk_size, (i + 1) * chunk_size) for i in range(num_chunks)]

    # Extend last chunk to include remainder.
    if num_values % num_chunks:
        chunks[-1] = (chunks[-1][0], num_values)

    return chunks
