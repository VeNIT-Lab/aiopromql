from result_schema import PrometheusResponseModel


class PrometheusClientBase:
    def __init__(self, url: str):
        self.base_url = url

    def make_label_string(self, **labels) -> str:
        non_empty_labels = {k: v for k, v in labels.items() if v is not None}
        if not non_empty_labels:
            return ''
        label_parts = [f'{k}="{v}"' for k, v in non_empty_labels.items()]
        return '{' + ','.join(label_parts) + '}'

    def _parse_response(self, response: dict) -> PrometheusResponseModel:
        return PrometheusResponseModel(**response)
