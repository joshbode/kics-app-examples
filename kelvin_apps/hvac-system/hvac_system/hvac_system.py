"""
Data Application.
"""

from kelvin.app import DataApplication


class App(DataApplication):
    """Application."""

    def process(self) -> None:
        print(self.data)

