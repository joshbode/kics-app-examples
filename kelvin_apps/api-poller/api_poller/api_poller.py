from kelvin.app import DataApplication
import requests


class App(DataApplication):

    def call_api(self):
        """
        Call the openweathermap API and same the `temp_f` variable into our buffer
        """

        base_url = self.config.base_url
        params = {
            "appid": self.config.appid,
            "q": self.config.query
        }

        with requests.get(base_url, params=params) as response:
            try:
                temp_kelvin = response.json()['main']['temp']
            except KeyError:
                self.logger.warn(f'Not a valid request response, exiting. {response.json()}')
                return

        self.logger.info('temp_kelvin', temp_kelvin=temp_kelvin)
        temp_f = round(((9 / 5) * (temp_kelvin - 273) + 32), 1)

        self.make_message("raw.float32", 'temp_f', store=True, value=temp_f)

    def output_avg_temp(self):
        """
        Calculate the mean temperature and emit the value
        """

        # Check that we have enough data as defined in the `topics` section of our app.yaml
        if self.data_status != {}:
            self.logger.warning(f"DATA STATUS ERROR : {self.data_status}")
            return

        # compute mean
        mn = self.data['temp_f'].series().mean()
        self.logger.info(f'mean temp_f:{mn}')

        # Create and emit message
        msg = self.make_message("raw.float32", name='avg_temp', value=mn)
        self.emit(msg)

    def process(self):
        """
        Main run function
        """
        self.call_api()
        self.output_avg_temp()
