"""
Data Application.
"""
import csv
from typing import List

from kelvin.app import DataApplication


class InjectionEntryData:
    index: int
    gas_flow: float
    valve_state: int

    def __init__(self, item: list) -> None:
        index_value, gas_flow_value, valve_state_value = item
        self.index = int(index_value) if index_value else 0
        self.gas_flow = float(gas_flow_value) if gas_flow_value else -1.0
        self.valve_state = int(valve_state_value) if valve_state_value else -1


class App(DataApplication):
    """Application."""

    loaded_data: List
    counter = 0
    limit = 0

    def init(self) -> None:
        """
        Initialization method
        """
        self.logger.info("Initialising")
        file_path: str = self.config.data_file_path
        with open(file_path, "rt") as file:
            # Retrieve all data
            data = csv.reader(file)
            # Drop the header
            real_data = list(data)[1:]
            self.loaded_data = [InjectionEntryData(item=item) for item in real_data]
            self.limit = len(self.loaded_data)

    def process(self) -> None:
        """Process data."""
        self.logger.info("Data", data=self.data)
        if 0 <= self.counter < self.limit:
            entry: InjectionEntryData = self.loaded_data[self.counter]
            self.logger.info(f"Emitting new entry: (gas flow) {entry.gas_flow} | (valve state) {entry.valve_state}")
            self.make_message(
                type="raw.float32",
                name="gas_flow",
                value=entry.gas_flow,
                emit=True,
                _asset_name='emulation'
            )
            self.make_message(
                type="raw.int32",
                name="valve_state",
                value=entry.valve_state,
                emit=True,
                _asset_name='emulation'
            )
            self.counter += 1
        else:
            self.logger.info("Restarting cycle..")
            self.counter = 0
