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
        # IMPORTANT - There are two ways to access credentials:

        # 1 - Pass specific credentials as environment variables the @app.yaml
        # @app.yaml -> system -> environment_vars
        # and access them with the following:
        username = os.getenv("KELVIN_USERNAME", "fail_user")
        password = os.getenv("KELVIN_PASSWORD", "fail_password")
        self.logger.debug("Username", username=username)
        self.logger.debug("Password", password=password)
        self.client.login(password=password)

        # OR

        # 2 - kelvin-sdk will automatically provide your kelvin credentials into the container
        # and automatically inject them in the Kelvin-sdk-client object.
        # Simply invoke:
        # self.client.login()

        # Finally access your data
        acp_data = self.client.acp.list_acp()
        self.logger.info("ACP Data", acp_data=str(acp_data))

    def process(self) -> None:
        """Process data."""