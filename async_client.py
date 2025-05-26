import httpx
from datetime import datetime
from base import PrometheusClientBase,PrometheusResponseModel


class PrometheusAsync(PrometheusClientBase):
    def __init__(self, url: str):
        super().__init__(url)
        self.client = httpx.AsyncClient(base_url=url)
        self.client.timeout = httpx.Timeout(2.0)

    async def query(self, promql: str) -> PrometheusResponseModel:
        response = await self.client.get("/api/v1/query", params={"query": promql})
        response.raise_for_status()
        return self._parse_response(response.json())

    async def query_range(
        self,
        promql: str,
        start: datetime,
        end: datetime,
        step: str = "30s",
    ) -> PrometheusResponseModel:
        start_ts = start.timestamp()
        end_ts = end.timestamp()

        response = await self.client.get(
            "/api/v1/query_range",
            params={
                "query": promql,
                "start": start_ts,
                "end": end_ts,
                "step": step
            }
        )
        response.raise_for_status()
        return self._parse_response(response.json())

    async def aclose(self):
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.client.aclose()
