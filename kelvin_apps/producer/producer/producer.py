"""
Data Application.
"""

import random

from kelvin.app import DataApplication


class App(DataApplication):

    enabled: bool = False
    min_value: int = 0
    max_value: int = 1000

    def init(self) -> None:
        # To access the declared inputs
        self.logger.info("Inputs", inputs=self.interface.inputs)
        # To access the declared outputs
        self.logger.info("Outputs", outputs=self.interface.outputs)
        # To access the configuration block under app->kelvin-configuration
        self.logger.info("Configurations", configurations=self.config)
        # To access the complete app configuration i.e. app.yaml
        self.logger.info("Complete configurations", complete_configurations=self.app_configuration)
        self.logger.info("Data", data=self.data)
        self.enabled = self.config.enabled
        if self.enabled:
            self.min_value = self.config.min
            self.max_value = self.config.max
            if self.min_value is None or self.max_value is None:
                self.logger.warning("Missing configuration keys (min/max).")
        else:
            self.logger.info("Data Generation is disabled.")

    def process(self) -> None:
        """
        Process data
        """
        # Get app configurations
        if self.enabled:
            for metric in self.interface.outputs:
                value = random.uniform(self.min_value, self.max_value)
                self.emit_message(self.interface.outputs[metric], value)

    def emit_message(self, metric, value):
        # Create message
        message = self.make_message(
            metric.data_type,
            name=metric.name,
            value=round(value, 2)
        )
        self.logger.info("Published value: ", message=str(message))
        self.emit(message)
