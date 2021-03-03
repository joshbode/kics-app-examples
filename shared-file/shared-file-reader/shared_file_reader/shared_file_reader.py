"""
Data Application.
"""

from kelvin.app import DataApplication


class App(DataApplication):
    """Application."""

    def process(self) -> None:
        """Process data."""
        try:
            with open("/shared-data/data.log", "r") as resultFile:
                # Print the last line
                lastLine = str(list(resultFile)[-1]).replace('\n', ''.replace('\r', ''))
                print(f"The last line read from the shared file: {lastLine}")
        except:
            pass

