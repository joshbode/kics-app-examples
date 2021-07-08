"""
Data Application.
"""

from kelvin.app import DataApplication
from kelvin.message.raw import Float32
from kelvin.message.raw import Int32
import random


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


    def process(self) -> None:
        """Process data."""
        # Get app configurations
        enabled = self.config.enabled
        if enabled:
            min_value = self.config.min
            max_value = self.config.max
            if min_value is None or max_value is None:
                print('Missing configuration keys (min/max).')
                return
            for metric in self.interface.outputs:
                value = random.uniform(min_value, max_value)
                self.emit_message(self.interface.outputs[metric], value)
        else:
            print('Data Generation is disabled.')



    def emit_message(self, metric, value):
        # Create message
        msg = self.make_message(
            metric.data_type,
            name=metric.name,
            value=round(value, 2)
        )
        print('[ Published:')
        print('[ ' + metric.data_type + ' -> timestamp: ' + str(msg._.time_of_validity*1e-9))
        print('[ name: ' + metric.name)
        print('[ value: ' + str(msg.value))
        # Emit message
        self.emit(msg)