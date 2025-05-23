from prometheus_connect import PrometheusClient
from datetime import datetime, timedelta
from datetime import timezone
from result_schema import PrometheusResponseModel , Metric , TimeSeries

def print_query_dict(results:dict[Metric,TimeSeries]):
    for metric,timeseries in results.items():
        print(f"Total timeseries points for metric: {metric.get("__name__")} is {len(timeseries)}")
        print(f"Node: {metric.get("nodename")} -> {timeseries.latest().value} , ts: {timeseries.latest().timestamp}")


if __name__ == "__main__":
    # Constants
    URL: str = f"http://10.42.0.1:30090/api/v1"
    end =  datetime.now(timezone.utc)
    start = end- timedelta(minutes=5)
    
    #logic
    pq = PrometheusClient(URL)
    promql_query = "node_filesystem_avail_bytes{mountpoint='/'}/1000^3 * on(pod) group_left(nodename) node_uname_info"
    matrix_results : PrometheusResponseModel= pq.query_range(promql_query,start,end,)
    vector_results : PrometheusResponseModel= pq.query(promql_query)
    matrix_dict:dict[Metric,TimeSeries] = matrix_results.to_metric_map()
    vector_dict: dict[Metric,TimeSeries] = vector_results.to_metric_map()

    print_query_dict(matrix_dict)
    print_query_dict(vector_dict)
    print("done")