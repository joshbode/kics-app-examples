# KSOS App Examples

This repository contains a set of application examples for the KSOS platform.

# Example structure #

### **Generic Applications** ### 

* **Flask Server** - Python WebServer utility, running with python 3.6 on port 5000 (see 'system' under *app.yaml*)
* **InfluxDB** - Base InfluxDB application with custom configurations (see 'system' under *app.yaml*)
* **Nginx** - A InfluxDB application with custom configurations (see 'system' under *app.yaml*)

### **Kelvin Applications** ### 

* **API Poller** - A simple Kelvin Application showcasing API communication with python's requests library
* **Producer** - A producer application that emits several temperatures and measure (float32) values.
* **Consumer** - A consumer application that subscribes to the values emitted by the **producer** application.
* **Kelvin Client Integration** - A Kelvin App that showcases its integration with Kelvin-SDK-Client for tailored access to platform data.
* **Min-Max Configuration** - An application that showcases custom threshold configuration (see 'app->kelvin-configuration' under **app.yaml**)
* **Valve Malfunction** - An application that process gas flow data into a Valve Malfunction Model
* **Weather** - An application that subscribes to temperature data with retention features and emits calculated values based on the inputs.

### **Use Cases** ### 

* **Vehicle Image Detection** - A trio of applications (2 Kelvin Applications, 1 Generic Application) showcasing a simple image recognition scenario.
* **Shared File Application** - An example on how to share files & volumes locally in the Emulation System

Additional documentation can be found on: [docs.kelvininc.com](https://docs.kelvininc.com)