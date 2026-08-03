"""
Metric Model for Project Astra.
Represents metric measurements (counters, gauges, latency histograms).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional
import time


class MetricType(str, Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"


@dataclass
class Metric:
    """
    Represents an individual metric measurement.
    """
    name: str
    value: float
    metric_type: MetricType = MetricType.GAUGE
    unit: str = ""
    tags: Dict[str, str] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "metric_type": self.metric_type.value if isinstance(self.metric_type, MetricType) else self.metric_type,
            "unit": self.unit,
            "tags": self.tags,
            "timestamp": self.timestamp
        }
