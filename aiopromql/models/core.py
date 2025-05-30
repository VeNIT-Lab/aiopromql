"""
Generic data structures for modeling time series and labeled metrics.
"""

from datetime import datetime
from typing import Dict, List, NamedTuple


class MetricLabelSet:
    """
    Hashable wrapper around a Prometheus metric label dictionary.

    Prometheus metrics are identified by a set of key-value labels
    (e.g., {"job": "api", "instance": "localhost:9090"}). This class allows such
    a label set to be used as a key in Python dictionaries by making it hashable
    and comparable.

    Instances of this class are used as keys in the dictionary returned by
    `PrometheusResponseModel.to_metric_map()`, where each MetricLabelSet maps to
    a TimeSeries object.
    """

    def __init__(self, metric: Dict[str, str]):
        self.dict = metric
        self._key = frozenset(metric.items())

    def __hash__(self) -> int:
        return hash(self._key)

    def __eq__(self, other) -> bool:
        if not isinstance(other, MetricLabelSet):
            return False
        return self._key == other._key

    def __repr__(self) -> str:
        return f"MetricLabelSet({self.dict})"

    def get(self, label: str, default=None):
        """
        Return the value for the given label key, or default if not present.

        :param label: The label key to retrieve from the metric dictionary.
        :type label: str
        :param default: The value to return if the label is not found. Defaults to None.
        :return: The value corresponding to the label, or the default if label is missing.
        :rtype: str or Any
        """
        return self.dict.get(label, default)


class TimeSeriesPoint(NamedTuple):
    """
    A single timestamped data point from a Prometheus time series.

    Represents one (timestamp, value) pair, where the timestamp is a `datetime`
    object and the value is a float. Useful for building time series from Prometheus
    query results.
    """

    timestamp: datetime
    value: float

    @classmethod
    def from_prometheus_value(cls, ts: float, value: str) -> "TimeSeriesPoint":
        """
        Converts a Prometheus response (timestamp, value) pair to TimeSeriesPoint.

        Args:
            ts: Epoch timestamp.
            value: String representation of float value.

        Returns:
            A TimeSeriesPoint instance.
        """
        return cls(datetime.fromtimestamp(ts), float(value))

    def __str__(self):
        return f"{self.timestamp.isoformat()} → {self.value:.2f}"


class TimeSeries:
    """
    A sequence of timestamped float values (TimeSeriesPoint) with utility methods.

    This class abstracts a Prometheus time series and provides methods for inspection,
    aggregation, and manipulation. Used in `PrometheusResponseModel.to_metric_map()`
    where each MetricLabelSet maps to a TimeSeries.
    """

    def __init__(self, values: List[TimeSeriesPoint]):
        """
        Args:
            values: List of initial TimeSeriesPoint objects.
        """
        self.values: List[TimeSeriesPoint] = values

    def __iter__(self):
        return iter(self.values)

    def __len__(self):
        return len(self.values)

    def __getitem__(self, idx) -> TimeSeriesPoint:
        return self.values[idx]

    def __repr__(self):
        return f"{self.values}"

    def add_point(self, point: TimeSeriesPoint):
        """Adds a new data point."""
        self.values.append(point)

    def extend(self, other: "TimeSeries"):
        """Appends another TimeSeries' points to this one."""
        self.values.extend(other.values)

    def latest(self) -> TimeSeriesPoint | None:
        """Returns the latest (most recent) data point."""
        return max(self.values, key=lambda x: x.timestamp, default=None)

    def average(self) -> float | None:
        """Computes the average of all values."""
        nums = [v.value for v in self.values if isinstance(v.value, (int, float))]
        return sum(nums) / len(nums) if nums else None
