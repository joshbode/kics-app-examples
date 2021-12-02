"""
Data Application.
"""

import random

from kelvin.sdk.app import DataApplication


class App(DataApplication):
    """Application."""

    def process(self) -> None:
        """Process data."""

        # Generate a random value
        value = random.randint(0, 5000)
        print(f"Writing to shared file the following value: {value}")
        try:
            # Append the random value to the shared file
            with open("/opt/kelvin/app/data/buffer_file.log", "w") as resultFile:
                resultFile.write(f"{value}\n")
        except Exception as exc:
            print(f"Error writing to file: {exc}")
