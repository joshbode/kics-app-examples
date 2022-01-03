# Valve Malfunction

This example showcases a valve malfunction detection scenario.  
The **injector** application will output `gas_flow` and `valve_state` values from a data file under `data/data.csv`.  
The second application, **valve-malfunction**, will collect those values and determine whether there's a malfunction.

## 1. The injector application

1. Under `valve-malfunction-injector/` run `kelvin app build --verbose`  
2.  Run `kelvin emulation start --show-logs`


## 2. The valve malfunction detection application

1. Under `valve-malfunction/` run `kelvin app build --verbose`  
2.  Run `kelvin emulation start --show-logs`



