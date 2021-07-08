"""
Data Application.
"""

from kelvin.app import DataApplication


class App(DataApplication):
    """Application."""

    TOPICS = {
        'raw.float32.#': {
            'target': '{name}',
            'storage_type': 'buffer',
            'storage_config': {'window': {'seconds': 10}, 'getter': 'value'},
        }
    }

    def process(self) -> None:
        """Process data."""
        # self.logger.info("config", config=self.config)
        # self.logger.info("frame", frame=frame)
        temperature = self.data.get("temperature", None)
        humidity = self.data.get("temperature", None)

        self.logger.info("temperature", data=temperature)
        self.logger.info("humidity", data=humidity)

        frame = self.frame

        if not frame.empty:
            temperature_mean = frame['temperature'].mean()
            humidity_mean = frame['humidity'].mean()

            temperature_message = self.make_message(
                'raw.float32',
                'temperature_mean',
                value=temperature_mean,
                time_of_validity=self.last_time_of_validity,
                emit=True
            )
            self.logger.info("temperature_mean", message=temperature_message)
            humidity_message = self.make_message(
                'raw.float32',
                'humidity_mean',
                value=humidity_mean,
                time_of_validity=self.last_time_of_validity,
                emit=True
            )
            self.logger.info("humidity_men", message=humidity_message)
