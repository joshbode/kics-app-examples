"""
Data Application.
"""
import base64
import tempfile
from pathlib import Path
from typing import Any

import numpy as np
from kelvin.app import DataApplication
from keras.models import load_model
from keras.preprocessing.image import load_img


class App(DataApplication):
    trained_model: str = "data/model_saved.h5"
    model: Any
    thresholds = [
        (0.0, 0.15, "definitely a CAR"),
        (0.15, 0.30, "most likely a CAR"),
        (0.70, 0.85, "most likely a PLANE"),
        (0.85, 1.0, "definitely a PLANE")
    ]

    def init(self) -> None:
        self.logger.info(f"Initialising -> {self.trained_model}")
        self.model = load_model(self.trained_model)

    def process(self) -> None:
        if self.data.get("vehicle_image", None):
            # 1 - read the latest image value
            vehicle_image = self.data.vehicle_image.value
            base64_bytes = vehicle_image.encode('ascii')
            message_bytes = base64.b64decode(base64_bytes)
            # 2 - load it into a temporary file
            with tempfile.NamedTemporaryFile(mode="wb") as vehicle_image_file:
                vehicle_image_file.write(message_bytes)
                # 3 - work the image
                image = load_img(Path(vehicle_image_file.name).absolute(), target_size=(227, 227))
                img = np.array(image)
                img = img / 255.0
                img = img.reshape(1, 227, 227, 3)
                label = self.model.predict(img)
                # 4 - predict its results
                prediction_result = label[0][0]
                # 5 - yield the final result
                self.logger.info(self.get_result(value=prediction_result))
                vehicle_image_file.close()

    def get_result(self, value: float) -> str:
        """
        Yield the "pretty" string from the calculated result.

        Returns
        -------
        str:
           the message to be displayed in the logs
        """
        for item in self.thresholds:
            min_value, max_value, desc = item
            if min_value <= value <= max_value:
                return desc
        return "No conclusion can be derived"
