from typing import Dict

from aiopromql import PrometheusSync
from aiopromql.models.core import MetricLabelSet, TimeSeries
from aiopromql.models.prometheus import PrometheusResponseModel

# Connect to Prometheus synchronously
with PrometheusSync("https://demo.promlabs.com") as client:
    # Run an range query for "up"
    resp: PrometheusResponseModel = client.query("up[1m]")
    # Convert response to a map of metrics to timeseries
    metric_map: Dict[MetricLabelSet, TimeSeries] = resp.to_metric_map()

    # Iterate over each metric label set and corresponding timeseries
    for metric_labels, timeseries in metric_map.items():
        # Print metric labels as dictionary
        print(f"Metric: {metric_labels.dict}")
        print("Time Series:")
        # print each point in time series
        for point in timeseries:
            print(point)
        print("#####################################")
