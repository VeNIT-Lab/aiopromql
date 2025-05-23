from typing import Dict, List, Tuple, Union, Literal
from pydantic import BaseModel
from collections import defaultdict
from datetime import datetime
from typing import NamedTuple
from typing import List, Union


# Your wrapper class
class Metric:
    def __init__(self, metric: Dict[str, str]):
        self.dict = metric
        self._key = frozenset(metric.items())

    def __hash__(self) -> int:
        return hash(self._key)

    def __eq__(self, other) -> bool:
        if not isinstance(other, Metric):
            return False
        return self._key == other._key

    def __repr__(self) -> str:
        return f"MetricKeyWrapper({self.dict})"

    def get(self, label: str, default=None):
        return self.dict.get(label, default)
    

class TimeSeriesPoint(NamedTuple):
    timestamp: datetime
    value: float


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

    def add(self, timestamp:datetime, value:float):
        self.values.append(TimeSeriesPoint(timestamp, value))

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

class MatrixDataModel(BaseModel):
    resultType: Literal["matrix"]
    result: List[MatrixResultModel]

class PrometheusResponseModel(BaseModel):
    status: Literal["success"]
    data: Union[VectorDataModel, MatrixDataModel]

    def _convert_value(self, t: float, v: str,):
        ts = datetime.fromtimestamp(t) 
        val = float(v)
        return ts, val

    def to_metric_map(
        self,
    ) -> Dict[Metric, TimeSeries]:
        metric_map: Dict[Metric, TimeSeries] = defaultdict(lambda: TimeSeries([]))

        if self.data.resultType == "vector":
            for r in self.data.result:
                key = Metric(r.metric)
                ts_val = self._convert_value(*r.value,)
                metric_map[key].add(*ts_val)
        elif self.data.resultType == "matrix":
            for r in self.data.result:
                key = Metric(r.metric)
                for val in r.values:
                    ts_val = self._convert_value(*val, )
                    metric_map[key].add(*ts_val)

        return dict(metric_map)