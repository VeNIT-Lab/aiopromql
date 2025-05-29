def make_label_string(negate_keys=None, **labels) -> str:
    """
    Return PromQL label selector string from provided labels.

    negate_keys: iterable of keys whose match should be negated (using !=).
    labels: key=value pairs for labels.
    """
    negate_keys = set(negate_keys or [])
    # Filter out None values
    filtered = {k: v for k, v in labels.items() if v is not None}
    if not filtered:
        return ""
    parts = []
    for k, v in filtered.items():
        op = "!=" if k in negate_keys else "="
        parts.append(f'{k}{op}"{v}"')
    return "{" + ",".join(parts) + "}"
