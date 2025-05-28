Welcome to aiopromql's documentation!
================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   usage
   api
   contributing

Introduction
------------

aiopromql is a minimalist Prometheus HTTP client for Python that supports both synchronous and asynchronous querying. It provides a clean, Pythonic model layer for Prometheus query responses and convenient helpers for mapping metrics into structured time series.

Features
--------

* Sync and async Prometheus client interfaces via ``httpx``
* Pydantic models for Prometheus vector and matrix responses
* Time series utilities and hashable metric keys
* Zero dependencies outside of ``httpx`` and ``pydantic``

Quick Start
----------

.. code-block:: python

    from aiopromql import PrometheusSync

    client = PrometheusSync("http://localhost:9090")
    resp = client.query('up')
    metric_map = resp.to_metric_map()

    for labels, series in metric_map.items():
        print(f"Labels: {labels.dict}")
        for point in series:
            print(f"  {point}")

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search` 