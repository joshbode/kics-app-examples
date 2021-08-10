"""
Data Application.
"""

import os
from datetime import datetime

from kelvin.app import DataApplication
from kelvin.sdk.client.model.requests import DataLabelCreate, DataLabelSource, Metric
from kelvin.sdk.client.model.requests import Type


class App(DataApplication):
    """Application."""

    url: str
    username: str
    password: str

    acp_name: str
    metric_source: str
    metric_key: str
    metric_type: str
    threshold: float
    label_name: str

    def init(self) -> None:
        """
        Initialisation method
        """
        # Initialize all environment values
        self.logger.info("Initialisation config: ", config=str(self.config))

        # Properties to identify the metric that will be associated to the Data Label
        self.acp_name = os.environ.get("ACP_NAME", 'fallback')
        self.metric_source = os.environ.get("METRIC_SOURCE", 'fallback')
        self.metric_key = os.environ.get("METRIC_KEY", 'fallback')
        self.metric_type = os.environ.get("METRIC_TYPE", 'fallback')

        # The label that the Data Label will be associated to
        self.label_name = os.environ.get("LABEL_NAME", 'fallback')

        # Threshold to evaluate the metric
        self.threshold = float(os.environ.get("METRIC_THRESHOLD", 'fallback'))

        # Environment to authenticate in
        self.url = os.environ.get("URL", 'fallback')

        # Initialize user credentials for authentication from Secrets
        # self.username = os.environ.get("DLSUSER", 'fallback')
        # self.password = os.environ.get("DLPASSWORD", 'fallback')

        try:
            self.client.login()
        except Exception as e:
            self.logger.error(f"Unable to authenticate.", error=str(e))

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
            self.logger.error("Unable to create Data Label.", error=str(e))

    def process(self) -> None:
        """Process data."""

        # Get input value
        input_metric = self.data.input_metric.value if self.data.get("input_metric", None) else None

        if not input_metric:
            self.logger.warning("Metric Value does not exist")
            return

        # Evaluate if a Data Label will be emitted
        if input_metric >= self.threshold:
            message = f"Metric value {input_metric} is above threshold of {self.threshold}. Creating Data Label..."
            self.logger.info(message)
            current_date = datetime.now()
            self.create_data_label(
                start_date=current_date
            )
        else:
            self.logger.warning(f"Metric value {input_metric} is below threshold of {self.threshold}.")
