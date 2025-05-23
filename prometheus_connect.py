import httpx
from typing import Optional
from datetime import datetime,timezone,timedelta

from result_schema import PrometheusResponseModel

class PrometheusClient:
    URL: str = f"http://10.42.0.1:30090/api/v1"

    def _query(self, promql: str) -> dict:
        with httpx.Client() as client:
            response = client.get(f"{self.URL}/query", params={"query": promql})
            response.raise_for_status()
            return response.json()

    def _query_range(
    self,
    promql: str,
    start: datetime | None = None,
    end: datetime | None = None,
    step: str = "30s", 
) -> dict:
        if not (start and end):
            raise ValueError("Both 'start' and 'end' must be provided for range queries")

        start_ts = start.isoformat()
        end_ts = end.isoformat()

        with httpx.Client() as client:
            response = client.get(
                f"{self.URL}/query_range",
                params={
                    "query": promql,
                    "start": start_ts,
                    "end": end_ts,
                    "step": step
                }
            )
            response.raise_for_status()
            return response.json()
    
    
    def make_label_string(self,**labels):
        non_empty_labels = {k: v for k, v in labels.items() if v is not None}
        if not non_empty_labels:
            return ''
        label_parts = [f'{k}="{v}"' for k, v in non_empty_labels.items()]
        return '{' + ','.join(label_parts) + '}'
    
    def _parse_response(self,response:dict)-> PrometheusResponseModel:
        return PrometheusResponseModel(**response)
