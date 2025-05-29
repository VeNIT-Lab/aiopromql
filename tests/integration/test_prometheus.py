import asyncio
import os
from datetime import datetime, timedelta, timezone

import pytest

from aiopromql import PrometheusAsync, PrometheusSync, make_label_string

# Get Prometheus URL from environment variable!
PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "http://localhost:9090")

# Common Prometheus metrics to test
PROMETHEUS_METRICS = [
    "up",
    "prometheus_build_info",
    "prometheus_http_requests_total",
    "prometheus_http_request_duration_seconds_count",
    "go_goroutines",
    "go_threads",
]


@pytest.mark.integration
def test_sync_query():
    """Test synchronous query."""
    client = PrometheusSync(PROMETHEUS_URL)

    # Test instant query
    resp = client.query("up")
    assert resp is not None
    metric_map = resp.to_metric_map()
    assert len(metric_map) > 0
    assert any("job" in labels.dict for labels in metric_map.keys())

    # Test range query
    end = datetime.now(tz=timezone.utc)
    start = end - timedelta(minutes=5)
    resp = client.query_range("up", start=start, end=end, step="1m")
    assert resp is not None
    metric_map = resp.to_metric_map()
    assert len(metric_map) > 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_async_query():
    """Test asynchronous query."""
    async with PrometheusAsync(PROMETHEUS_URL) as client:
        # Test instant query
        resp = await client.query("prometheus_build_info")
        assert resp is not None
        metric_map = resp.to_metric_map()
        assert len(metric_map) > 0
        assert any("job" in labels.dict for labels in metric_map.keys())

        # Test range query
        end = datetime.now(tz=timezone.utc)
        start = end - timedelta(minutes=5)
        resp = await client.query_range("prometheus_http_requests_total", start=start, end=end, step="1m")
        assert resp is not None
        metric_map = resp.to_metric_map()
        assert len(metric_map) > 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_concurrent_queries():
    """Test concurrent queries."""
    async with PrometheusAsync(PROMETHEUS_URL) as client:
        tasks = [client.query(metric) for metric in PROMETHEUS_METRICS]
        responses = await asyncio.gather(*tasks)

        for metric, resp in zip(PROMETHEUS_METRICS, responses):
            assert resp is not None, f"Failed to get response for {metric}"
            metric_map = resp.to_metric_map()
            assert len(metric_map) > 0, f"No data found for {metric}"


@pytest.mark.integration
def test_metric_labels():
    """Test querying metrics with specific labels."""
    client = PrometheusSync(PROMETHEUS_URL)

    # Query with specific label
    labels = make_label_string(negate_keys=["job"], job="")
    resp = client.query(f"up{labels}")
    assert resp is not None
    metric_map = resp.to_metric_map()
    assert len(metric_map) > 0
    assert all("job" in labels.dict for labels in metric_map.keys())


@pytest.mark.integration
@pytest.mark.asyncio
async def test_rate_query():
    """Test rate queries."""
    async with PrometheusAsync(PROMETHEUS_URL) as client:
        # Query rate of HTTP requests
        resp = await client.query("rate(prometheus_http_requests_total[1m])")
        assert resp is not None
        metric_map = resp.to_metric_map()
        assert len(metric_map) > 0
