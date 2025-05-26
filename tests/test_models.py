from datetime import datetime, timedelta

import pytest

from aiopromql.models.core import (
    MetricLabelSet,
    TimeSeries,
    TimeSeriesPoint,
)


@pytest.mark.unit
def test_metriclabelset_eq():
    m1 = MetricLabelSet({"a": "1", "b": "2"})
    m2 = MetricLabelSet({"b": "2", "a": "1"})  # same items different order
    m3 = MetricLabelSet({"a": "1"})
    assert m1 == m2
    assert m1 != m3
    assert m1 != {"a": "1", "b": "2"}  # different type


@pytest.mark.unit
def test_timeseries_iter_len_getitem():
    now = datetime.now()
    points = [
        TimeSeriesPoint(now, 1.0),
        TimeSeriesPoint(now + timedelta(seconds=1), 2.0),
        TimeSeriesPoint(now + timedelta(seconds=2), 3.0),
    ]
    ts = TimeSeries(points)
    # __iter__ returns an iterator over points
    assert list(iter(ts)) == points
    # __len__ returns number of points
    assert len(ts) == len(points)
    # __getitem__ returns the right point
    assert ts[0] == points[0]
    assert ts[2] == points[2]
