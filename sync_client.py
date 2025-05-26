import httpx 
from datetime import datetime
from base import PrometheusClientBase , PrometheusResponseModel


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
