"""
Data Application.
"""

from kelvin.app import DataApplication
from kelvin.icd import Message
from kelvin.message.raw import Float32
from kelvin.message.raw import Int32
from typing import Sequence


class App(DataApplication):


    def init(self) -> None:
        # To access the declared inputs
        print('\nInputs: ' + str(self.interface.inputs))
        # To access the declared outputs
        print('\nOutputs: ' + str(self.interface.outputs))
        # To access the configuration block under app->kelvin-configuration
        print('\nConfigurations: ' + str(self.config))
        # To access the complete app configuration i.e. app.yaml
        print('\nComplete app configuration: ' + str(self.app_configuration))
        print('\nData: ' + str(self.data))


    def process_data(self, data: Sequence[Message]) -> None:
        # Process input messages
        for msg in data:
            print('[ Received:')
            print('[ ' + msg._.type + ' -> timestamp: ' + str(msg._.time_of_validity * 1e-9))
            print('[ name: ' + msg._.name)
            print('[ value: ' + str(msg.value))

            # Check for specific Inputs and generate new metrics
            if 'temperature_in_celsius' in msg._.name:
                temperature_in_fahrenheit = (msg.value * 9 / 5) + 32
                if isinstance(msg, Float32):
                    name = "temperature_in_fahrenheit"
                    value = round(temperature_in_fahrenheit, 2)
                    self.make_message("raw.float32", name, value, emit=True)
                elif isinstance(msg, Int32):
                    name = "temperature_in_fahrenheit_int"
                    value = int(temperature_in_fahrenheit)
                    self.make_message("raw.int32", name, value, emit=True)
                else:
                    print('Unsupported message type: ' + str(msg.type))
                    return
            elif 'measure_in_cm' in msg._.name:
                measure_in_inches = msg.value / 2.54
                if isinstance(msg, Float32):
                    name = "measure_in_inches"
                    value = round(measure_in_inches, 2)
                    self.make_message("raw.float32", name, value, emit=True)
                elif isinstance(msg, Int32):
                    name = "measure_in_inches_int"
                    value = int(measure_in_inches)
                    self.make_message("raw.int32", name, value, emit=True)
                else:
                    print('Unsupported message type: ' + str(msg.type))
                    return
            else:
                print('Discarding message: ' + str(msg._.name))
                return

            print('[ Published:')
            print('[ name: ' + name)
            print('[ value: ' + str(value))
