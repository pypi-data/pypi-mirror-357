from fastapi_mvp.settings import Settings


class MetricsSettings(Settings):
    excluded_handlers: list[str]
    latency_lowr_buckets: list[float]
