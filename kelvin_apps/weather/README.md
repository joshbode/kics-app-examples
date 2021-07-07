## Weather custom datamodel application

This example will show how to:
    - Inject custom datamodel data

Check [Kelvin documentation](https://docs.kelvininc.com/latest/documentation/sdk/package_and_emulate_apps/inject_and_extract_data/?h=+custom+#inject-custom-datamodel-data-example) for more details.


#### Build and emulate

Open a terminal and run:
```bash
kelvin app build
kelvin emulation start --verbose --show-logs
```

#### Inject data

Open another terminal and run:

```bash
kelvin emulation inject data/data.csv --period=1 --endpoint opc.tcp://weathersource:48010 --repeat --app-name weather-custom-datamodel:1.0.0
```
