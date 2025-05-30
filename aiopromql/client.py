import warnings
from datetime import datetime
from typing import Optional, Union

import httpx

from .models.prometheus import PrometheusResponseModel


class PrometheusClientBase:
    """Base Prometheus client with common utilities."""

    def __init__(self, url: str):
        self.base_url = url

    def _parse_response(self, response: dict) -> PrometheusResponseModel:
        """Parse Prometheus JSON response into model."""
        return PrometheusResponseModel(**response)


class PrometheusSync(PrometheusClientBase):
    """Synchronous Prometheus client using httpx."""

    def __init__(self, url: str, timeout: Optional[float] = 2.0):
        super().__init__(url)
        self.session = httpx.Client(timeout=httpx.Timeout(timeout))

    def query(self, promql: str, raw: bool = False) -> Union[PrometheusResponseModel, dict]:
        """
        Run an instant PromQL query.

        :param promql: The PromQL query string to execute.
        :param raw: If True, return raw JSON response as dict; otherwise parse into model.
        :return: Parsed Prometheus response model or raw JSON dict.
        :raises httpx.HTTPStatusError: If HTTP response status is 4xx or 5xx.
        :raises httpx.RequestError: If a network error occurs.
        """
        response = self.session.get(f"{self.base_url}/api/v1/query", params={"query": promql})
        response.raise_for_status()
        data = response.json()
        return data if raw else self._parse_response(data)

    def query_range(
        self,
        promql: str,
        start: datetime,
        end: datetime,
        step: str = "30s",
        raw: bool = False,
    ) -> Union[PrometheusResponseModel, dict]:
        """
        Run a ranged PromQL query over a time window.

        :param promql: The PromQL query string to execute.
        :param start: Start datetime of the query range.
        :param end: End datetime of the query range.
        :param step: Query resolution step width (e.g., '30s', '1m').
        :param raw: If True, return raw JSON response as dict; otherwise parse into model.
        :return: Parsed Prometheus response model or raw JSON dict.
        :raises httpx.HTTPStatusError: If HTTP response status is 4xx or 5xx.
        :raises httpx.RequestError: If a network error occurs.
        """
        start_ts = start.timestamp()
        end_ts = end.timestamp()
        response = self.session.get(
            f"{self.base_url}/api/v1/query_range",
            params={"query": promql, "start": start_ts, "end": end_ts, "step": step},
        )
        response.raise_for_status()
        data = response.json()
        return data if raw else self._parse_response(data)

    def close(self):
        """Close the sync client session."""
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def __del__(self):
        if not self.session.is_closed:
            warnings.warn("PrometheusSync was not closed. Use 'with' statement or call .close()")
        self.close()


class PrometheusAsync(PrometheusClientBase):
    """Asynchronous Prometheus client using httpx."""

    def __init__(self, url: str, timeout: Optional[float] = 2.0):
        super().__init__(url)
        self.client = httpx.AsyncClient(base_url=url, timeout=httpx.Timeout(timeout))

    async def query(self, promql: str, raw: bool = False) -> Union[PrometheusResponseModel, dict]:
        """
        Run an instant PromQL query asynchronously.

        :param promql: The PromQL query string to execute.
        :param raw: If True, return raw JSON response as dict; otherwise parse into model.
        :return: Parsed Prometheus response model or raw JSON dict.
        :raises httpx.HTTPStatusError: If HTTP response status is 4xx or 5xx.
        :raises httpx.RequestError: If a network error occurs.
        """
        response = await self.client.get("/api/v1/query", params={"query": promql})
        response.raise_for_status()
        data = response.json()
        return data if raw else self._parse_response(data)

    async def query_range(
        self,
        promql: str,
        start: datetime,
        end: datetime,
        step: str = "30s",
        raw: bool = False,
    ) -> Union[PrometheusResponseModel, dict]:
        """
        Run a ranged PromQL query over a time window asynchronously.

        :param promql: The PromQL query string to execute.
        :param start: Start datetime of the query range.
        :param end: End datetime of the query range.
        :param step: Query resolution step width (e.g., '30s', '1m').
        :param raw: If True, return raw JSON response as dict; otherwise parse into model.
        :return: Parsed Prometheus response model or raw JSON dict.
        :raises httpx.HTTPStatusError: If HTTP response status is 4xx or 5xx.
        :raises httpx.RequestError: If a network error occurs.
        """
        start_ts = start.timestamp()
        end_ts = end.timestamp()
        response = await self.client.get(
            "/api/v1/query_range",
            params={"query": promql, "start": start_ts, "end": end_ts, "step": step},
        )
        response.raise_for_status()
        data = response.json()
        return data if raw else self._parse_response(data)

    async def aclose(self):
        """Close the async client session."""
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.aclose()

    def __del__(self):
        if not self.client.is_closed:
            warnings.warn("PrometheusAsync was not closed. Use 'async with' or call 'await .aclose()'")
