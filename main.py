from prometheus_connect import PrometheusClient
from result_schema import PrometheusResponseModel
if __name__ == "__main__":
    pq = PrometheusClient()

    vector = pq._query("up")
    matrix  = pq._query("up[5m]")
    histogram = pq._query("coredns_dns_response_size_bytes_bucket")
    test = pq._query("count_values('instance', up)")
    parsed_matrix = PrometheusResponseModel(**matrix).to_metric_map()

    for key,val in parsed_matrix.items():
        print(key,val)

    print(matrix)    