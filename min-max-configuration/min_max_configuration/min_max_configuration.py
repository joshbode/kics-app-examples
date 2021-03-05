import random

from kelvin.app import DataApplication
from kelvin.message.raw import Float32

class App(DataApplication):
    """Application."""

    def process(self):
        temperature = self.data.get('temperature')
        min_threshold = self.config.complex_config.min_threshold
        max_threshold = self.config.complex_config.max_threshold
        if temperature and min_threshold <= temperature <= max_threshold:
            print(self.config.complex_config.success_message)
        else:
            print(random.choice(self.config.complex_config.rejection_messages))
