from datetime import datetime, timedelta, timezone
import asyncio

from client import PrometheusSync, PrometheusAsync
from models.core import MetricLabelSet, TimeSeries
from models.prometheus import PrometheusResponseModel

# Constants
URL: str = f"http://10.8.0.26:30090"
e =  datetime.now(timezone.utc)
st = e- timedelta(minutes=5)


def print_query_dict(results:dict[MetricLabelSet,TimeSeries]):
    for metric,timeseries in results.items():
        print(f"Total timeseries points for metric: {metric.get("__name__")} is {len(timeseries)}")
        print(f"Node: {metric.get("nodename")} -> {timeseries.latest().value} , ts: {timeseries.latest().timestamp}")

def test_sync_print(pq:PrometheusSync):
    promql_query = "node_filesystem_avail_bytes{mountpoint='/'}/1000^3 * on(pod) group_left(nodename) node_uname_info"
    matrix_results : PrometheusResponseModel= pq.query_range(promql_query,st,e,)
    vector_results : PrometheusResponseModel= pq.query(promql_query)
    matrix_dict:dict[MetricLabelSet,TimeSeries] = matrix_results.to_metric_map()
    vector_dict: dict[MetricLabelSet,TimeSeries] = vector_results.to_metric_map()

    print_query_dict(matrix_dict)
    print_query_dict(vector_dict)

async def test_async():
    async with PrometheusAsync(URL) as prom:
        tasks = [prom.query(f"up") for i in range(20)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        latest_res = list(results[-1].to_metric_map().items())[-1]
        print(f"sucessfulyl got {len(results)} results, latest is {latest_res}")

def test_sync():
    results:list[PrometheusResponseModel] = []
    for i in range(20):
        pq = PrometheusSync(URL)
        res = pq.query("up")
        results.append(res)
    latest_res = list(results[-1].to_metric_map().items())[-1]
    print(f"sucessfulyl got {len(results)} results, latest is {latest_res}")

if __name__ == "__main__":
    import time

    print("------ Running Sync ------")
    start = time.time()
    test_sync()
    print(f"Sync took {time.time() - start:.2f} seconds")

    print("------ Running Async ------")
    start = time.time()
    asyncio.run(test_async())
    print(f"Async took {time.time() - start:.2f} seconds")
    
