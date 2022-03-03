# Weather API Bridge

## Obtain an API token

[Sign Up](https://home.openweathermap.org/users/sign_up) to OpenWeatherMap for
a free account and get your [API key](https://home.openweathermap.org/api_keys)
and update `test.yaml`:

```yaml
app:
  bridge:
    configuration:
      connection:
        base_url: https://api.openweathermap.org/data/2.5
        api_key: your_key_here
```


## Building and Testing

1. Build the bridge:

  ```sh
  $ kelvin app build
  ```

2. Run the bridge in the Kelvin emulation system:

  ```sh
  $ kelvin emulation start --app-config test.yaml --show-logs
  ...
  ```

3. Use a tool like [`mqttui`](https://github.com/EdJoPaTo/mqttui) or [MQTT
   X](https://mqttx.app/) to connect to the MQTT broker to observe the messages
   that are generated.

   e.g. Find the emulation broker port and connect with `mqttui`:

    ```sh
    $ docker port kelvin-mqtt-broker.app 1883/tcp
    0.0.0.0:49153
    $ export PORT=49153
    $ mqttui -p ${PORT}
    ...
    ```

4. Shut down the emulation system to stop the bridge:

  ```sh
  $ kelvin emulation stop
  ```
