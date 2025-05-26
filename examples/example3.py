import asyncio
from aiopromql import PrometheusAsync


async def main():
    async with PrometheusAsync("http://10.42.0.1:30090") as client:
        queries = ["up", "process_cpu_seconds_total", "node_memory_MemAvailable_bytes"]
        tasks = [client.query(q) for q in queries]
        responses = await asyncio.gather(*tasks)

        for query, resp in zip(queries, responses):
            print(f"Results for query: {query}")
            metric_map = resp.to_metric_map()
            for labels, series in metric_map.items():
                print(f"  Labels: {labels.dict}")
                for point in series:
                    print(f"    {point}")


asyncio.run(main())
