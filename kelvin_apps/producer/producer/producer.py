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
        print('\nInputs: ' + str(self.interface.inputs))
        # To access the declared outputs
        print('\nOutputs: ' + str(self.interface.outputs))
        # To access the configuration block under app->kelvin-configuration
        print('\nConfigurations: ' + str(self.config))
        # To access the complete app configuration i.e. app.yaml
        print('\nComplete app configuration: ' + str(self.app_configuration))
        print('\nData: ' + str(self.data))
        self.enabled = self.config.enabled
        if self.enabled:
            self.min_value = self.config.min
            self.max_value = self.config.max
            if self.min_value is None or self.max_value is None:
                print('Missing configuration keys (min/max).')
        else:
            print('Data Generation is disabled.')

    def process(self) -> None:
        """Process data."""
        # Get app configurations
        if self.enabled:
            for metric in self.interface.outputs:
                value = random.uniform(self.min_value, self.max_value)
                self.emit_message(self.interface.outputs[metric], value)

    def emit_message(self, metric, value):
        # Create message
        msg = self.make_message(
            metric.data_type,
            name=metric.name,
            value=round(value, 2)
        )
        print('[ Published:')
        print('[ ' + metric.data_type + ' -> timestamp: ' + str(msg._.time_of_validity * 1e-9))
        print('[ name: ' + metric.name)
        print('[ value: ' + str(msg.value))
        # Emit message
        self.emit(msg)
