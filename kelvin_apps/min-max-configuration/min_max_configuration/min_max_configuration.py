import random

from kelvin.app import DataApplication


class App(DataApplication):
    """Application."""

    def process(self):
        temperature = self.data.get('temperature')
        min_threshold = self.config.min_threshold
        max_threshold = self.config.max_threshold
        if temperature and min_threshold <= temperature <= max_threshold:
            self.logger.info("Success message: ", message=self.config.success_message)
        else:
            self.logger.warning("Rejection message: ", message=random.choice(self.config.rejection_messages))
