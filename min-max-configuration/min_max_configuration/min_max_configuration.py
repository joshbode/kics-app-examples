import random

from kelvin.app import DataApplication


class App(DataApplication):
    """Application."""

    def process(self):
        temperature = self.data.get('temperature')
        min_threshold = self.config.min_threshold
        max_threshold = self.config.max_threshold
        if temperature and min_threshold <= temperature <= max_threshold:
            print(self.config.success_message)
        else:
            print(random.choice(self.config.rejection_messages))
