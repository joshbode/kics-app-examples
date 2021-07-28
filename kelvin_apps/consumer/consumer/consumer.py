"""
Data Application.
"""

from kelvin.app import DataApplication
from kelvin.message.raw import Float32
from kelvin.message.raw import Int32


class App(DataApplication):

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

    def process(self) -> None:
        try:
            self.logger.info("Received new data: ", data=self.data)
            temperature_in_celsius = self.data.get("temperature_in_celsius", None)
            if temperature_in_celsius:
                temperature_in_fahrenheit = (temperature_in_celsius.value * 9 / 5) + 32
                if isinstance(temperature_in_celsius._.type, Float32):
                    name = "temperature_in_fahrenheit"
                    value = round(temperature_in_fahrenheit, 2)
                    self.make_message("raw.float32", name, value, emit=True)
                elif isinstance(temperature_in_celsius._.type, Int32):
                    name = "temperature_in_fahrenheit_int"
                    value = int(temperature_in_fahrenheit)
                    self.make_message("raw.int32", name, value, emit=True)

            measure_in_cm = self.data.get("measure_in_cm", None)
            if measure_in_cm:
                measure_in_inches = measure_in_cm.value / 2.54
                if isinstance(measure_in_cm._.type, Float32):
                    name = "measure_in_inches"
                    value = round(measure_in_inches, 2)
                    self.make_message("raw.float32", name, value, emit=True)
                elif isinstance(measure_in_cm._.type, Int32):
                    name = "measure_in_inches_int"
                    value = int(measure_in_inches)
                    self.make_message("raw.int32", name, value, emit=True)
            self.logger.info("Dispatching new values...")
        except Exception as exc:
            self.logger.error("Error processing value: ", error=exc)
