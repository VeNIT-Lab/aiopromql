from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from aiopromql import PrometheusAsync, PrometheusSync, make_label_string
from aiopromql.models.core import MetricLabelSet, TimeSeries, TimeSeriesPoint
from aiopromql.models.prometheus import VectorDataModel, VectorResultModel
from tests.constants import (
    MOCK_PROMETHEUS_MATRIX_RESPONSE,
    MOCK_PROMETHEUS_VECTOR_RESPONSE,
)


@pytest.mark.unit
def test_make_label_string():
    assert make_label_string(foo="bar", baz=None) == '{foo="bar"}'
    assert make_label_string() == ""
    assert make_label_string(a="1", b="2") in ('{a="1",b="2"}', '{b="2",a="1"}')


@pytest.mark.unit
@patch("aiopromql.client.httpx.Client.get")
def test_sync_query_calls(mock_get):
    client = PrometheusSync("http://test")
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "status": "success",
        "data": {"resultType": "vector", "result": []},
    }
    mock_resp.raise_for_status = MagicMock()
    mock_get.return_value = mock_resp

    # test raw=False returns parsed model
    res = client.query("up", raw=False)
    assert hasattr(res, "to_metric_map")

    # test raw=True returns raw dict
    raw_res = client.query("up", raw=True)
    assert isinstance(raw_res, dict)

    client.close()


@pytest.mark.unit
@patch("aiopromql.client.httpx.Client.get")
def test_sync_query_range_calls(mock_get):
    client = PrometheusSync("http://test")

    mock_resp = MagicMock()
    mock_resp.json.return_value = MOCK_PROMETHEUS_MATRIX_RESPONSE
    mock_resp.raise_for_status = MagicMock()
    mock_get.return_value = mock_resp

    start = datetime.fromtimestamp(1748269440, tz=timezone.utc)
    end = datetime.fromtimestamp(1748269560, tz=timezone.utc)

    # Test raw=True returns raw dict
    res = client.query_range("up", start=start, end=end, step="60s", raw=True)
    assert isinstance(res, dict)
    assert res["data"]["resultType"] == "matrix"

    # Test raw=False returns parsed model
    res = client.query_range("up", start=start, end=end, step="60s", raw=False)
    assert hasattr(res, "to_metric_map")
    assert isinstance(res.to_metric_map(), dict)

    client.close()


@pytest.mark.unit
@pytest.mark.asyncio
@patch("aiopromql.client.httpx.AsyncClient.get", new_callable=AsyncMock)
async def test_async_query_calls(mock_get):
    client = PrometheusAsync("http://test")

    mock_resp = AsyncMock()
    mock_resp.json = MagicMock(return_value=MOCK_PROMETHEUS_VECTOR_RESPONSE)

    mock_resp.raise_for_status = MagicMock()
    mock_get.return_value = mock_resp

    res = await client.query("up", raw=True)
    assert isinstance(res, dict)
    assert res["status"] == "success"
    assert res["data"]["resultType"] == "vector"

    res = await client.query("up", raw=False)
    assert hasattr(res, "to_metric_map")
    assert isinstance(res.to_metric_map(), dict)
    assert res.data.result[0].metric.get("__name__") == "up"

    # close the client
    await client.aclose()
    # assert client.client.is_closed is True
    assert client.client.is_closed


@pytest.mark.unit
@pytest.mark.asyncio
async def test_query_with_context_manager():
    mock_response = AsyncMock()
    mock_response.json = MagicMock(return_value=MOCK_PROMETHEUS_VECTOR_RESPONSE)
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.aclose = AsyncMock()
        mock_client.is_closed = False

        async def close_and_set_flag():
            mock_client.is_closed = True

        mock_client.aclose.side_effect = close_and_set_flag  # to simulate closing the client

        mock_client_cls.return_value = mock_client

        async with PrometheusAsync("http://localhost:9090") as client:
            result = await client.query("up")

            # Assertions
            mock_client.get.assert_awaited_once_with("/api/v1/query", params={"query": "up"})
            assert result.data.result[0].metric.get("__name__") == "up"

        mock_client.aclose.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
@patch("aiopromql.client.httpx.AsyncClient.get", new_callable=AsyncMock)
async def test_async_query_range(mock_get):
    client = PrometheusAsync("http://test")

    mock_resp = AsyncMock()
    mock_resp.json = MagicMock(return_value=MOCK_PROMETHEUS_MATRIX_RESPONSE)
    mock_resp.raise_for_status = MagicMock()
    mock_get.return_value = mock_resp

    start = datetime.fromtimestamp(1748269440, tz=timezone.utc)
    end = datetime.fromtimestamp(1748269560, tz=timezone.utc)

    res = await client.query_range("up", start=start, end=end, step="60s", raw=True)
    assert isinstance(res, dict)
    assert res["data"]["resultType"] == "matrix"
    assert res["data"]["result"][0]["metric"]["__name__"] == "up"

    res = await client.query_range("up", start=start, end=end, step="60s", raw=False)
    assert hasattr(res, "to_metric_map")
    assert isinstance(res.to_metric_map(), dict)
    assert len(res.data.result) == 1

    # close the client
    await client.aclose()
    # assert client.client.is_closed is True
    assert client.client.is_closed


@pytest.mark.unit
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


@pytest.mark.unit
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
