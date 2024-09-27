import logging

from rich.logging import RichHandler


logging.basicConfig(
    level=logging.INFO, format="%(message)s", datefmt="[%X]", handlers=[RichHandler()]
)

log = logging.getLogger("gil-perf")
