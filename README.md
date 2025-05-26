# aiopromql

**aiopromql** is a minimalist Prometheus HTTP client for Python that supports both synchronous and asynchronous querying. It provides a clean, Pythonic model layer for Prometheus query responses and convenient helpers for mapping metrics into structured time series.

---

## 🚀 Features

- Sync and async Prometheus client interfaces via `httpx`
- Pydantic models for Prometheus vector and matrix responses
- Time series utilities and hashable metric keys
- Zero dependencies outside of `httpx` and `pydantic`

---

## 📦 Installation

```bash
pip install aiopromql
```

---

## 🔧 Basic Usage

### Synchronous Query

```python
from aiopromql import PrometheusSync

client = PrometheusSync("http://localhost:9090")

resp = client.query('up')
metric_map = resp.to_metric_map()

for labels, series in metric_map.items():
    print(f"Labels: {labels.dict}")
    for point in series:
        print(f"  {point}")
```

### Ranged Query

```python
from datetime import datetime, timedelta

end = datetime.utcnow()
start = end - timedelta(hours=1)

resp = client.query_range('up', start=start, end=end, step='60s')
metric_map = resp.to_metric_map()

# Same access pattern as before
```

### Asynchronous Query

```python
import asyncio
from aiopromql import PrometheusAsync

async def main():
    async with PrometheusAsync("http://localhost:9090") as client:
        queries = ['up', 'process_cpu_seconds_total', 'node_memory_MemAvailable_bytes']
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
```
## Development
```
# Install dev tools
pip install -e .[dev]

# Run tests
pytest

# Format & lint
ruff format
ruff check aiopromql

# Build
hatch build
```
---


## Acknowledgments:

This project is used in the DECICE — [DEVICE-EDGE-CLOUD Intelligent Collaboration framEwork](https://www.decice.eu/) — aiming to bridge HPC cloud and edge orchestration.

Special thanks to the [VeNIT Lab](https://venit.org/) and [other partners](https://www.decice.eu/consortium/) for their support and collaboration.

## 📄 License

MIT