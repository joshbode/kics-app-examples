"""
Data Application.
"""

import os
from typing import Any
from datetime import datetime
from kelvin.app import DataApplication
from kelvin.sdk.client import Client
from kelvin.sdk.client.model.requests import Type
from kelvin.sdk.client.model.requests import DataLabelCreate, DataLabelSource, Metric


class App(DataApplication):
    """Application."""
    
    client: any
    acp_name: str
    metric_source: str
    metric_key: str
    metric_type: str
    threshold: float
    label_name: str

    def on_initialize(self, *args: Any, **kwargs: Any) -> bool:
        super().on_initialize(*args, **kwargs)
        self.init()
        return True

    def init(self) -> None:
        """
        Initialisation method
        """

        print('on_initialize config ' + str(self.config))

        #Initialize all environment values
        #Properties to identify the metric that will be associated to the Datalabel
        self.acp_name = os.environ.get("ACP_NAME", 'fallback')
        self.metric_source = os.environ.get("METRIC_SOURCE", 'fallback')
        self.metric_key = os.environ.get("METRIC_KEY", 'fallback')
        self.metric_type = os.environ.get("METRIC_TYPE", 'fallback')

        #The label that the Datalabel will be associated to
        self.label_name = os.environ.get("LABEL_NAME", 'fallback')

        #Threshold to evaluate the metric
        self.threshold = float(os.environ.get("METRIC_THRESHOLD", 'fallback'))

        #Environment to authenticate in
        self.url = os.environ.get("URL", 'fallback')

        #Initialize user credentials for authentication from Secrets
        self.username = os.environ.get("DLSUSER", 'fallback')
        self.password = os.environ.get("DLPASSWORD", 'fallback')
        
        #Authenticate on the Platform
        try:

            self.client = Client.from_file(
                url=self.url,
                username=self.username
            )
            self.client.login(password=self.password)
        except Exception as e:
            print(f"Unable to authenticate. Error: {str(e)}")

        return True
    
    def create_data_label(self, start_date):
        try:
            metrics = [
                Metric(
                        acp_name=self.acp_name,
                        source=self.metric_source,
                        key=self.metric_key,
                        type=self.metric_type
                )
            ]
            
            source = DataLabelSource(
                type=Type.workload,
                info={
                    'name': self.metric_source
                }
            )

            label_create = DataLabelCreate(
                label_name=self.label_name,
                end_date=start_date,
                start_date=start_date,
                source=source,
                metrics=metrics
            )
            self.client.data_label.create_data_label(
                data=label_create
            )
        except Exception as e:
            print(f"Unable to create Datalabel. Error: {str(e)}")

    def process(self) -> None:
        """Process data."""

        #Get input value
        input_metric = self.data.input_metric.value if self.data.get("input_metric", None) else None

        if not input_metric:
            print("Metric Value does not exist")
            return

        #Evaluate if a datalabel will be emitted 
        if input_metric >= self.threshold:
            print(f"Metric value {input_metric} is above threshold of {self.threshold}. Creating Data Label...")
            current_date = datetime.now()
            self.create_data_label(
                start_date=current_date
            )
        else:
            print(f"Metric value {input_metric} is below threshold of {self.threshold}.")
            


