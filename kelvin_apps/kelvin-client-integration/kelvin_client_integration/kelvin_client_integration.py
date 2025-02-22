"""
Data Application.
"""
import os

from kelvin.app import DataApplication


class App(DataApplication):
    """Application."""

    def init(self) -> None:
        """
        Initialization method
        """
        # 1 - To access the complete application configuration file, i.e. the contents of the 'app.yaml':
        # self.app_configuration

        # 2 - To access the inputs and outputs, respectively:
        # self.interface.inputs
        # and
        # self.interface.outputs

        self.logger.info("Initialising")

        # Access credentials
        username = os.getenv("KELVIN_USERNAME", "fail_user")
        password = os.getenv("KELVIN_PASSWORD", "fail_password")
        self.logger.info("Username", username=username)
        self.logger.info("Password", password=password)
        # Authenticate and retrieve data
        self.client.login(password=password)
        acp_data = self.client.acp.list_acp()
        self.logger.info("ACP Data", acp_data=str(acp_data))

    def process(self) -> None:
        """Process data."""
        # 1 - To access the input data:
        # self.data

        # 2 - Considering your data is defined in the inputs as 'my_var', you can access it with:
        # my_var = self.data.my_var
        # or
        # my_var = self.data.get('my_var')

        # 4 - Build a message to emit:
        """
        self.logger.info("Data", data=self.data)
        message = self.make_message(
            "raw.float32",
            name="my_new_var",
            value=1.0,
            time_of_validity=int(1 * 1e9),
            emit=False
        )
        """
        # 5 - Emit the message
        # self.emit(message)

