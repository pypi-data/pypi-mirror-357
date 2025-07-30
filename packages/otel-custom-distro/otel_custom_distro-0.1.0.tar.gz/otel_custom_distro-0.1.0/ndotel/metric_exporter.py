from opentelemetry.sdk.metrics.export import (
    MetricExporter,
    MetricExportResult,
    AggregationTemporality,
)
from typing import Sequence, Optional

try:
    # For newer versions (1.12.0+)
    from opentelemetry.sdk.metrics._internal.point import Metric
except ImportError:
    # For older versions
    from opentelemetry.sdk.metrics._internal.export import Metric as Metric

class MyMetricExporter(MetricExporter):
    def export(
        self,
        metrics: Sequence[Metric],
        timeout_millis: Optional[float] = None,
        **kwargs
    ) -> MetricExportResult:
        for metric in metrics:
            points = getattr(metric, 'data', getattr(metric, 'points', []))
            for point in points:
        return MetricExportResult.SUCCESS

    def shutdown(self, timeout_millis: Optional[float] = None, **kwargs) -> None:
        return True

    def force_flush(self, timeout_millis: Optional[float] = None) -> bool:
        return True

    def aggregation_temporality(
        self, instrument_type
    ) -> AggregationTemporality:
        return AggregationTemporality.CUMULATIVE
