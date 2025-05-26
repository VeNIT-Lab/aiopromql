import httpx 
from datetime import datetime
from models.prometheus import PrometheusResponseModel

class PrometheusClientBase:
    def __init__(self, url: str):
        self.base_url = url

    def make_label_string(self, **labels) -> str:
        non_empty_labels = {k: v for k, v in labels.items() if v is not None}
        if not non_empty_labels:
            return ''
        label_parts = [f'{k}="{v}"' for k, v in non_empty_labels.items()]
        return '{' + ','.join(label_parts) + '}'

    def _parse_response(self, response: dict) -> PrometheusResponseModel:
        return PrometheusResponseModel(**response)

class PrometheusSync(PrometheusClientBase):
    def query(self, promql: str) -> PrometheusResponseModel:
        with httpx.Client() as client:
            response = client.get(f"{self.base_url}/api/v1/query", params={"query": promql})
            response.raise_for_status()
            return self._parse_response(response.json())

    def query_range(
        self,
        promql: str,
        start: datetime,
        end: datetime,
        step: str = "30s",
    ) -> PrometheusResponseModel:
        start_ts = start.timestamp()
        end_ts = end.timestamp()

        with httpx.Client() as client:
            response = client.get(
                f"{self.base_url}/api/v1/query_range",
                params={
                    "query": promql,
                    "start": start_ts,
                    "end": end_ts,
                    "step": step
                }
            )
            response.raise_for_status()
            return self._parse_response(response.json())


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
