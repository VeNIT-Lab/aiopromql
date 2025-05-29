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
        :type promql: str
        :param raw: If True, return raw JSON response as dict; otherwise parse into model.
        :type raw: bool
        :return: Parsed Prometheus response or raw JSON dict.
        """
        response = self.session.get(f"{self.base_url}/api/v1/query", params={"query": promql})
        response.raise_for_status()
        return response.json() if raw else self._parse_response(response.json())

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
        :type promql: str
        :param start: Start datetime of the query range.
        :type start: datetime.datetime
        :param end: End datetime of the query range.
        :type end: datetime.datetime
        :param step: Query resolution step width (e.g., '30s', '1m').
        :type step: str
        :param raw: If True, return raw JSON response as dict; otherwise parse into model.
        :type raw: bool
        :return: Parsed Prometheus response or raw JSON dict.
        """
        start_ts = start.timestamp()
        end_ts = end.timestamp()
        response = self.session.get(
            f"{self.base_url}/api/v1/query_range",
            params={"query": promql, "start": start_ts, "end": end_ts, "step": step},
        )
        response.raise_for_status()
        return response.json() if raw else self._parse_response(response.json())

    def close(self):
        """Close the sync client session."""
        self.session.close()

    def __del__(self):
        self.close()


class PrometheusAsync(PrometheusClientBase):
    """Asynchronous Prometheus client using httpx."""

    def __init__(self, url: str, timeout: Optional[float] = 2.0):
        super().__init__(url)
        self.client = httpx.AsyncClient(base_url=url, timeout=httpx.Timeout(timeout))

    async def query(self, promql: str, raw: bool = False) -> Union[PrometheusResponseModel, dict]:
        """
        Run an instant PromQL query.

        :param promql: The PromQL query string to execute.
        :type promql: str
        :param raw: If True, return raw JSON response as dict; otherwise parse into model.
        :type raw: bool
        :return: Parsed Prometheus response or raw JSON dict.
        """
        response = await self.client.get("/api/v1/query", params={"query": promql})
        response.raise_for_status()
        return response.json() if raw else self._parse_response(response.json())

    async def query_range(
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
        :type promql: str
        :param start: Start datetime of the query range.
        :type start: datetime.datetime
        :param end: End datetime of the query range.
        :type end: datetime.datetime
        :param step: Query resolution step width (e.g., '30s', '1m').
        :type step: str
        :param raw: If True, return raw JSON response as dict; otherwise parse into model.
        :type raw: bool
        :return: Parsed Prometheus response or raw JSON dict.
        """
        start_ts = start.timestamp()
        end_ts = end.timestamp()
        response = await self.client.get(
            "/api/v1/query_range",
            params={"query": promql, "start": start_ts, "end": end_ts, "step": step},
        )
        response.raise_for_status()
        return response.json() if raw else self._parse_response(response.json())

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
