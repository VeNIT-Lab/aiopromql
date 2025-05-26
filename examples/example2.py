from aiopromql.client import PrometheusSync

client = PrometheusSync("http://10.42.0.1:30090")

resp = client.query('up')
metric_map = resp.to_metric_map()

for labels, series in metric_map.items():
    print(f"Labels: {labels.dict}")
    for point in series:
        print(f"  {point}")