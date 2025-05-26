MOCK_PROMETHEUS_VECTOR_RESPONSE = {
    "status": "success",
    "data": {
        "resultType": "vector",
        "result": [
            {
                "metric": {
                    "__name__": "up",
                    "container": "prometheus",
                    "endpoint": "http-web",
                    "instance": "10.244.1.156:9090",
                    "job": "prometheus-stack-kube-prom-prometheus",
                    "namespace": "monitoring",
                    "pod": "prometheus-prometheus-stack-kube-prom-prometheus-0",
                    "service": "prometheus-stack-kube-prom-prometheus",
                },
                "value": [1748269310.899, "1"],
            },
        ],
    },
}

MOCK_PROMETHEUS_MATRIX_RESPONSE = {
    "status": "success",
    "data": {
        "resultType": "matrix",
        "result": [
            {
                "metric": {
                    "__name__": "up",
                    "container": "prometheus",
                    "endpoint": "http-web",
                    "instance": "10.244.1.156:9090",
                    "job": "prometheus-stack-kube-prom-prometheus",
                    "namespace": "monitoring",
                    "pod": "prometheus-prometheus-stack-kube-prom-prometheus-0",
                    "service": "prometheus-stack-kube-prom-prometheus",
                },
                "values": [[1748269440, "1"], [1748269560, "1"]],
            }
        ],
    },
}
