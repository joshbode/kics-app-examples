"""
Data Application.
"""
from functools import reduce

from kelvin.app import DataApplication
from typing.io import TextIO


class App(DataApplication):
    """Application."""

    file: TextIO

    def init(self) -> None:
        mode = "r"
        buffering = 1
        self.file = open(self.config.file_name, mode=mode, buffering=buffering)

    def process(self) -> None:
        """Process data."""
        try:
            last_line = reduce(lambda _, x: x, self.file, None)
            if last_line is not None:
                self.logger.info("The last line read from the shared file", last_line=last_line)
        except Exception as exc:
            self.logger.error(f"Error reading from file", exc=exc)
