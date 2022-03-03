# MQTT Bridge Example

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

  Note: the configuration for testing reuses the internal MQTT broker in place
  of an external broker to avoid having to set one up.

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

4. Push some data for the bridge to read from MQTT:

  ```sh
  $ mqttui publish -p ${PORT} \
    "Foo/SomeAsset" \
    '{"t": 0, "v": 1.5, "x": 1}'
  ```

5. Push some data for the bridge to write to MQTT:

  ```sh
  $ mqttui -p ${PORT} publish \
    "input/emulation/mqtt-bridge/some-asset/bar" \
    '{"name": "bar", "source": "emulation/somewhere", "target": "emulation/mqtt-bridge", "asset_name": "some-asset", "data_type": "raw.text", "timestamp": "2021-01-01T00:01:02.123456Z", "payload": {"value": "xxxy"}}'
  ```

6. Shut down the emulation system to stop the bridge:

  ```sh
  $ kelvin emulation stop
  ```
