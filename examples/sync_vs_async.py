import asyncio
from datetime import datetime, timedelta, timezone

from aiopromql import PrometheusAsync, PrometheusSync
from aiopromql.models.prometheus import PrometheusResponseModel

# Constants
URL: str = "https://demo.promlabs.com"
e = datetime.now(timezone.utc)
st = e - timedelta(minutes=5)


async def test_async():
    async with PrometheusAsync(URL) as prom:
        tasks = [prom.query("up") for i in range(20)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        latest_res = list(results[-1].to_metric_map().items())[-1]
        print(f"sucessfulyl got {len(results)} results, latest: \n{latest_res}")


def test_sync():
    results: list[PrometheusResponseModel] = []
    pq = PrometheusSync(URL)
    for i in range(20):
        res = pq.query("up")
        results.append(res)
    latest_res = list(results[-1].to_metric_map().items())[-1]
    print(f"sucessfulyl got {len(results)} results, latest: \n{latest_res}")


if __name__ == "__main__":
    import time

    print("Sending 20 queries sync vs async... ")

    print("------ Running Sync ------")
    start = time.time()
    test_sync()
    print(f"Sync took {time.time() - start:.2f} seconds")

    print("------ Running Async ------")
    start = time.time()
    asyncio.run(test_async())
    print(f"Async took {time.time() - start:.2f} seconds")
