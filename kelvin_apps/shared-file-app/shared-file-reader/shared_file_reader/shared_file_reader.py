"""
Data Application.
"""

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
            last_line = str(list(self.file)[-1]).replace('\n', ''.replace('\r', ''))
            print(f"The last line read from the shared file: {last_line}")
        except Exception as exc:
            print(f"Error reading from file: {exc}")
