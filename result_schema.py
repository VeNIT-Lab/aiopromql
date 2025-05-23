from typing import Dict, List, Tuple, Union, Literal
from pydantic import BaseModel
from collections import defaultdict
from datetime import datetime

# Your wrapper class
class Metric:
    def __init__(self, metric: Dict[str, str]):
        self.metric = metric
        self._key = frozenset(metric.items())

    def __hash__(self) -> int:
        return hash(self._key)

    def __eq__(self, other) -> bool:
        if not isinstance(other, Metric):
            return False
        return self._key == other._key

    def __repr__(self) -> str:
        return f"MetricKeyWrapper({self.metric})"

    def get(self, label: str, default=None):
        return self.metric.get(label, default)

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

    def _convert_value(self, t: float, v: str, time_as_datetime: bool, value_as_float: bool):
        ts = datetime.fromtimestamp(t) if time_as_datetime else t
        val = float(v) if value_as_float else v
        return ts, val

    def to_metric_map(
        self,
        time_as_datetime: bool = True,
        value_as_float: bool = True
    ) -> Dict[Metric, List[Tuple[Union[float, datetime], Union[str, float]]]]:
        metric_map: Dict[Metric, List[Tuple[Union[float, datetime], Union[str, float]]]] = defaultdict(list)

        if self.data.resultType == "vector":
            for r in self.data.result:
                key = Metric(r.metric)
                metric_map[key].append(self._convert_value(*r.value, time_as_datetime, value_as_float))
        elif self.data.resultType == "matrix":
            for r in self.data.result:
                key = Metric(r.metric)
                metric_map[key].extend(self._convert_value(*val, time_as_datetime, value_as_float) for val in r.values)

        return dict(metric_map)