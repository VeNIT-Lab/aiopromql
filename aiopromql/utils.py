def make_label_string(**labels) -> str:
    """Return PromQL label selector string from provided labels."""
    non_empty_labels = {k: v for k, v in labels.items() if v is not None}
    if not non_empty_labels:
        return ""
    label_parts = [f'{k}="{v}"' for k, v in non_empty_labels.items()]
    return "{" + ",".join(label_parts) + "}"
