"""
Pydantic models for parsing and transforming Prometheus query json responses.
"""

from collections import defaultdict
from typing import Dict, List, Literal, Tuple, Union

from pydantic import BaseModel

from .core import MetricLabelSet, TimeSeries, TimeSeriesPoint


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
        Converts the response into a mapping from metric label sets to time series.

        The resulting data structure uses generic, reusable types:
        - MetricLabelSet: a hashable representation of metric labels.
        - TimeSeries: a sequence of timestamped values.

        Returns:
            A dictionary mapping MetricLabelSet to TimeSeries.
        """
        return self.data.to_metric_map()
