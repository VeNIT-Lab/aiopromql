import httpx
import asyncio
from datetime import datetime
from typing import Optional, Union

from .models.prometheus import PrometheusResponseModel


class PrometheusClientBase:
    """Base Prometheus client with common utilities."""
    def __init__(self, url: str):
        self.base_url = url

    def make_label_string(self, **labels) -> str:
        """Return PromQL label selector string from provided labels."""
        non_empty_labels = {k: v for k, v in labels.items() if v is not None}
        if not non_empty_labels:
            return ''
        label_parts = [f'{k}="{v}"' for k, v in non_empty_labels.items()]
        return '{' + ','.join(label_parts) + '}'

    def _parse_response(self, response: dict) -> PrometheusResponseModel:
        """Parse Prometheus JSON response into model."""
        return PrometheusResponseModel(**response)


class PrometheusSync(PrometheusClientBase):
    """Synchronous Prometheus client using httpx."""
    def __init__(self, url: str, timeout: Optional[float] = 2.0):
        super().__init__(url)
        self.session = httpx.Client(timeout=httpx.Timeout(timeout))

    def query(self, promql: str, raw: bool = False) -> Union[PrometheusResponseModel, dict]:
        """Run an instant PromQL query."""
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
        """Run a ranged PromQL query over a time window."""
        start_ts = start.timestamp()
        end_ts = end.timestamp()
        response = self.session.get(
            f"{self.base_url}/api/v1/query_range",
            params={"query": promql, "start": start_ts, "end": end_ts, "step": step}
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
        """Run an instant PromQL query."""
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
        """Run a ranged PromQL query over a time window."""
        start_ts = start.timestamp()
        end_ts = end.timestamp()
        response = await self.client.get(
            "/api/v1/query_range",
            params={"query": promql, "start": start_ts, "end": end_ts, "step": step}
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
            asyncio.create_task(self.aclose())
