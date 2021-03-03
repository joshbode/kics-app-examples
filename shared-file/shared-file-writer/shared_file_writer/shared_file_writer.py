"""
Data Application.
"""

from kelvin.app import DataApplication
import random


class App(DataApplication):
    """Application."""

    def process(self) -> None:
        """Process data."""

        # Generate a random value
        value = random.randint(0, 5000)
        print(f"Writing to shared file the following value: {value}")
        try:
            # Append the random value to the shared file
            with open("/shared-data/data.log", "a") as resultFile:
                resultFile.write(f"{value}\n")
        except:
            pass


