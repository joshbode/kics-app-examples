from kelvin.sdk.app import Application

"""
Valve malfunction model

Two inputs: gas_flow and valve_state

gas_flow is somewhat noisy, so we average the last 30 seconds of flow data to determine flow rate 

We'll flag a valve malfunction if valve_state is consistent for an entire 30 second period, but flow rate doesn't match

if valve_state = 0, we expect no flow
if valve_state = 1, we expect gas_flow

gas_flow threshold is defined in app.yaml
"""


class App(Application):

    def process(self) -> None:
        """
        Process Incoming Data for Valve Malfunction Model
        """
        if self.data_status != {}:
            self.logger.warning(f"DATA STATUS ERROR : {self.data_status}")
            return

        # get thresholds
        gas_flow_threshold = self.config.thresholds["gas_flow_threshold"].value

        # compute gas_flow time period average
        gas_flow = self.data.gas_flow.series()
        gas_flow_average_in_window = gas_flow.mean()

        # valve_state array, to ensure that it's consistent for entire period
        valve_values_in_window = self.data.valve_state.series()
        valve_set = set(valve_values_in_window)
        valve_value = bool(valve_values_in_window[0])

        self.logger.info(  # everything we want to log goes here
            "check",
            n_valve=len(valve_set),
            is_valve=valve_value,
            is_gas_above=gas_flow_average_in_window > gas_flow_threshold,
            len_gf=len(self.data.gas_flow)
        )

        # Model Logic
        if len(valve_set) == 1:  # Only one valve state in last 30s
            if (gas_flow_average_in_window > gas_flow_threshold) == valve_value:
                return  # alternatively, we could emit "normal" message or 0 value
            else:
                self.logger.info(f'EMITTING ALERT: valve_malfunction')
                self.message("raw.float32", name='valve_malfunction', value=1, emit=True, store=False)
