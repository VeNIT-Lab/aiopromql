from typing import Dict, List, Tuple, Union, Literal
from pydantic import BaseModel
from collections import defaultdict
from datetime import datetime
from typing import NamedTuple
from typing import List, Union


# Your wrapper class
class MetricLabelSet:
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
    timestamp: datetime
    value: float

    @classmethod
    def from_prometheus_value(cls, ts: float, value: str) -> "TimeSeriesPoint":
        return cls(datetime.fromtimestamp(ts), float(value))
    
    def __str__(self):
        return f"{self.timestamp.isoformat()} → {self.value:.2f}"


class TimeSeries:
    def __init__(self, values: List[TimeSeriesPoint]):
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
        self.values.append(point)

    def extend(self, other: 'TimeSeries'):
        self.values.extend(other.values)

    def latest(self)->TimeSeriesPoint|None:
        return max(self.values, key=lambda x: x.timestamp, default=None)

    def average(self)->float|None:
        nums = [v.value for v in self.values if isinstance(v.value, (int, float))]
        return sum(nums) / len(nums) if nums else None


# Prometheus response models
class VectorResultModel(BaseModel):
    metric: Dict[str, str]
    value: Tuple[float, str]

class MatrixResultModel(BaseModel):
    metric: Dict[str, str]
    values: List[Tuple[float, str]]

class VectorDataModel(BaseModel):
    resultType: Literal["vector"]
    result: List[VectorResultModel]

    def to_metric_map(self) -> Dict[MetricLabelSet, TimeSeries]:
        metric_map: Dict[MetricLabelSet, TimeSeries] = defaultdict(lambda: TimeSeries([]))

        for r in self.result:
            key = MetricLabelSet(r.metric)
            ts_point = TimeSeriesPoint.from_prometheus_value(*r.value)
            metric_map[key].add_point(ts_point)

        return dict(metric_map)

class MatrixDataModel(BaseModel):
    resultType: Literal["matrix"]
    result: List[MatrixResultModel]

    def to_metric_map(self) -> Dict[MetricLabelSet, TimeSeries]:
        metric_map: Dict[MetricLabelSet, TimeSeries] = defaultdict(lambda: TimeSeries([]))

        for r in self.result:
            key = MetricLabelSet(r.metric)
            for val in r.values:
                ts_point = TimeSeriesPoint.from_prometheus_value(*val)
                metric_map[key].add_point(ts_point)

        return dict(metric_map)

class PrometheusResponseModel(BaseModel):
    status: Literal["success"]
    data: Union[VectorDataModel, MatrixDataModel]

    def to_metric_map(self) -> Dict[MetricLabelSet, TimeSeries]:
        return self.data.to_metric_map()