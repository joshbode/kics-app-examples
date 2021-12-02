import base64
import os
import random
from pathlib import Path
from typing import List

from kelvin.app import DataApplication


class App(DataApplication):
    planes_image_dir: Path = Path("data/planes")
    cars_image_dir: Path = Path("data/cars")
    image_paths: List[Path] = []

    def init(self) -> None:
        """
        Initialization method
        """
        self.logger.info("Initialising")
        self.image_paths.extend([self.planes_image_dir / item for item in os.listdir(self.planes_image_dir)])
        self.image_paths.extend([self.cars_image_dir / item for item in os.listdir(self.planes_image_dir)])

    def process(self) -> None:
        """Process data."""
        if self.image_paths:
            # 1 - get a random index and publish the images randomly
            random_index = random.randint(0, len(self.image_paths) - 1)
            image = self.image_paths[random_index]
            # 2 - open the image and publish it
            with open(image, "rb") as original_file:
                encoded_image = base64.b64encode(original_file.read())
                encoded_image_message = encoded_image.decode("ascii")
                self.logger.info(f"Emitting image read from - {image.absolute()}")
                self.emit_value(name="vehicle_image", asset_name="emulation", value=encoded_image_message)
