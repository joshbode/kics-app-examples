"""
Data Application.
"""

from kelvin.sdk.app import DataApplication


class App(DataApplication):
    """Application."""

    def process(self) -> None:
        """Process data."""
        try:
            with open("data/buffer_file.log", "r") as resultFile:
                # Print the last line
                last_line = str(list(resultFile)[-1]).replace('\n', ''.replace('\r', ''))
                print(f"The last line read from the shared file: {last_line}")
        except Exception as exc:
            print(f"Error reading from file: {exc}")
