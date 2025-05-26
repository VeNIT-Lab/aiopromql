import pytest
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock, patch

from aiopromql.client import PrometheusSync, PrometheusAsync, PrometheusClientBase
from aiopromql.models.core import MetricLabelSet, TimeSeriesPoint, TimeSeries
from aiopromql.models.prometheus import VectorDataModel, VectorResultModel


def test_make_label_string():
    client = PrometheusClientBase("http://dummy")
    assert client.make_label_string(foo="bar", baz=None) == '{foo="bar"}'
    assert client.make_label_string() == ""
    assert client.make_label_string(a="1", b="2") in ('{a="1",b="2"}', '{b="2",a="1"}')


@patch("aiopromql.client.httpx.Client.get")
def test_sync_query_calls(mock_get):
    client = PrometheusSync("http://test")
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"status": "success", "data": {"resultType": "vector", "result": []}}
    mock_resp.raise_for_status = MagicMock()
    mock_get.return_value = mock_resp

    # test raw=False returns parsed model
    res = client.query("up", raw=False)
    assert hasattr(res, "to_metric_map")

    # test raw=True returns raw dict
    raw_res = client.query("up", raw=True)
    assert isinstance(raw_res, dict)

    client.close()



@pytest.mark.asyncio
@patch("aiopromql.client.httpx.AsyncClient.get", new_callable=AsyncMock)
async def test_async_query_calls(mock_get):
    client = PrometheusAsync("http://test")
    
    # Create a mock response object
    mock_resp = AsyncMock()
    
    # Mock .json() as a **regular method**, not async
    mock_resp.json = MagicMock(return_value={
        "status": "success",
        "data": {"resultType": "vector", "result": []},
    })
    
    # Mock .raise_for_status() as a **regular method**
    mock_resp.raise_for_status = MagicMock()
    
    mock_get.return_value = mock_resp
    
    # Now this won't raise 'coroutine was never awaited' or TypeErrors
    res = await client.query("up", raw=False)

def test_metric_label_set_and_timeseries():
    labels = {"foo": "bar"}
    mset = MetricLabelSet(labels)
    assert mset.get("foo") == "bar"
    assert mset.get("missing", "default") == "default"

    point = TimeSeriesPoint.from_prometheus_value(1680000000.0, "1.23")
    assert isinstance(point.timestamp.year, int)
    assert isinstance(point.value, float)

    ts = TimeSeries([])
    ts.add_point(point)
    assert len(ts) == 1
    assert ts.latest() == point
    assert ts.average() == point.value


def test_vector_data_model_to_metric_map():
    entry = VectorResultModel(metric={"job": "test"}, value=(1680000000.0, "2.5"))
    vector_data = VectorDataModel(resultType="vector", result=[entry])
    metric_map = vector_data.to_metric_map()
    assert isinstance(metric_map, dict)
    # keys should be MetricLabelSet
    for key in metric_map.keys():
        assert isinstance(key, MetricLabelSet)
    # values should be TimeSeries with at least one point
    for ts in metric_map.values():
        assert len(ts) > 0
