Usage Guide
===========

This guide provides examples of how to use aiopromql for both synchronous and asynchronous Prometheus queries.

Synchronous Usage
---------------

Basic Query
~~~~~~~~~~

.. code-block:: python

    from aiopromql import PrometheusSync

    # Initialize the client
    client = PrometheusSync("http://localhost:9090")

    # Execute a simple query
    resp = client.query('up')
    metric_map = resp.to_metric_map()

    # Process the results
    for labels, series in metric_map.items():
        print(f"Labels: {labels.dict}")
        for point in series:
            print(f"  {point}")

Range Query
~~~~~~~~~~

.. code-block:: python

    from datetime import datetime, timedelta, timezone

    # Set time range
    end = datetime.now(timezone.utc)
    start = end - timedelta(hours=1)

    # Execute range query
    resp = client.query_range('up', start=start, end=end, step='60s')
    metric_map = resp.to_metric_map()

    # Process results as before
    for labels, series in metric_map.items():
        print(f"Labels: {labels.dict}")
        for point in series:
            print(f"  {point}")

Asynchronous Usage
----------------

Basic Async Query
~~~~~~~~~~~~~~~

.. code-block:: python

    import asyncio
    from aiopromql import PrometheusAsync

    async def main():
        async with PrometheusAsync("http://localhost:9090") as client:
            # Execute multiple queries concurrently
            queries = ['up', 'process_cpu_seconds_total', 'process_resident_memory_bytes']
            tasks = [client.query(q) for q in queries]
            responses = await asyncio.gather(*tasks)

            # Process results
            for query, resp in zip(queries, responses):
                print(f"Results for query: {query}")
                metric_map = resp.to_metric_map()
                for labels, series in metric_map.items():
                    print(f"  Labels: {labels.dict}")
                    for point in series:
                        print(f"    {point}")

    asyncio.run(main())

Range Query with Async
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from datetime import datetime, timedelta, timezone
    from aiopromql import PrometheusAsync

    async def get_range_data():
        async with PrometheusAsync("http://localhost:9090") as client:
            end = datetime.now(timezone.utc)
            start = end - timedelta(hours=1)
            
            resp = await client.query_range('up', start=start, end=end, step='60s')
            return resp.to_metric_map()

    # Run the async function
    metric_map = asyncio.run(get_range_data()) 