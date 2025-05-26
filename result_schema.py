from typing import Dict, List, Tuple, Union, Literal
from pydantic import BaseModel
from collections import defaultdict
from datetime import datetime
from typing import NamedTuple
from typing import List, Union


# Your wrapper class
class MetricLabelSet:
    """Hashable wrapper around a Prometheus metric dict to be used as a dictionary key."""
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
        return self.dict.get(label, default)
    

class TimeSeriesPoint(NamedTuple):
    """A single timestamped float data point."""
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
    """A list of TimeSeriesPoints with utility methods."""
    def __init__(self, values: List[TimeSeriesPoint]):
        """
        Args:
            values: List of initial TimeSeriesPoint objects.
        """
        self.values : List[TimeSeriesPoint] = values

    def __iter__(self):
        return iter(self.values)

    def __len__(self):
        return len(self.values)

    def __getitem__(self, idx)->TimeSeriesPoint:
        return self.values[idx]

    def __repr__(self):
        return f"Values({self.values})"

    def add_point(self, point: TimeSeriesPoint):
        """Adds a new data point."""
        self.values.append(point)

    def extend(self, other: 'TimeSeries'):
        """Appends another TimeSeries' points to this one."""
        self.values.extend(other.values)

    def latest(self)->TimeSeriesPoint|None:
        """Returns the latest (most recent) data point."""
        return max(self.values, key=lambda x: x.timestamp, default=None)

    def average(self)->float|None:
        """Computes the average of all values."""
        nums = [v.value for v in self.values if isinstance(v.value, (int, float))]
        return sum(nums) / len(nums) if nums else None


# Prometheus response models
class VectorResultModel(BaseModel):
    """Single Prometheus vector result entry."""
    metric: Dict[str, str]
    value: Tuple[float, str]

class MatrixResultModel(BaseModel):
    """Single Prometheus matrix result entry."""
    metric: Dict[str, str]
    values: List[Tuple[float, str]]

class VectorDataModel(BaseModel):
    """Parsed vector data block from Prometheus."""
    resultType: Literal["vector"]
    result: List[VectorResultModel]

    def to_metric_map(self) -> Dict[MetricLabelSet, TimeSeries]:
        """
        Converts vector results to a dict of TimeSeries object grouped by metric labels.

        Returns:
            Dictionary mapping MetricLabelSet to TimeSeries.
        """
        metric_map: Dict[MetricLabelSet, TimeSeries] = defaultdict(lambda: TimeSeries([]))

        for r in self.result:
            key = MetricLabelSet(r.metric)
            ts_point = TimeSeriesPoint.from_prometheus_value(*r.value)
            metric_map[key].add_point(ts_point)

        return dict(metric_map)

class MatrixDataModel(BaseModel):
    """Parsed matrix data block from Prometheus."""
    resultType: Literal["matrix"]
    result: List[MatrixResultModel]

    def to_metric_map(self) -> Dict[MetricLabelSet, TimeSeries]:
        """
        Converts matrix results to a dict of TimeSeries grouped by metric labels.

        Returns:
            Dictionary mapping MetricLabelSet to TimeSeries.
        """
        metric_map: Dict[MetricLabelSet, TimeSeries] = defaultdict(lambda: TimeSeries([]))

        for r in self.result:
            key = MetricLabelSet(r.metric)
            for val in r.values:
                ts_point = TimeSeriesPoint.from_prometheus_value(*val)
                metric_map[key].add_point(ts_point)

        return dict(metric_map)

class PrometheusResponseModel(BaseModel):
    """Top-level Prometheus query response wrapper."""
    status: Literal["success"]
    data: Union[VectorDataModel, MatrixDataModel]

    def to_metric_map(self) -> Dict[MetricLabelSet, TimeSeries]:
        """
        Converts the response into a metric map, delegating to the underlying data type.

        Returns:
            Dictionary mapping MetricLabelSet to TimeSeries.
        """
        return self.data.to_metric_map()