import os
import datetime
import traceback
import json

import logging

from .store import Store
from .converter import Converter
from .metrics.network_analysis import NetworkAnalyzer as network_analyzer

logger = logging.getLogger(__name__)


class MetricComputer(Converter):
    """TODO"""

    def __init__(
        self,
        registered_reader_class,
        input_path,
        output_format,
        output_path,
        by_feeder,
        verbose=True,
        **kwargs
    ):
        """MetricComputer class CONSTRUCTOR."""
        self.by_feeder = by_feeder
        self.output_format = output_format
        # Call super
        super(MetricComputer, self).__init__(
            registered_reader_class,
            None,
            input_path,
            output_path,
            verbose=True,
            **kwargs
        )

    def convert(self):
        """Cannot call convert."""
        raise NotImplementedError(
            "MetricComputer cannot convert. Use Converter instead."
        )

    def compute(self):
        """Compute the metrics"""
        inputs = self.get_inputs(self.feeder)

        self.configure_reader(inputs)
        self.reader.parse(self.m)

        self.net = network_analyzer(self.m)
        self.net.model.set_names()
        # If we compute the metrics per feeder, we need to have the objects taged with their feeder_names
        if self.by_feeder:
            # Split the network into feeders (assumes objects have been taged)
            self.net.split_network_into_feeders()
            self.net.compute_all_metrics_per_feeder()
        else:
            self.net.compute_all_metrics()

        # Export to the required format
        if self.output_format.lower() == "json":
            self.net.export_json(os.path.join(self.output_path, "metrics.json"))
        elif self.output_format.lower() in ["xlsx", "excel", "xls"]:
            self.net.export(os.path.join(self.output_path, "metrics.xlsx"))
