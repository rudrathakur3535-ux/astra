"""
Performance Profiler & Optimization Recommender for Project Astra OS.
Profiles execution performance, calculates latency distributions (P50/P95/P99),
and automatically generates performance optimization suggestions.
"""

from typing import Dict, List, Any, Optional
import math
from app.observability.metrics_service import MetricsService


class PerformanceProfiler:
    """
    Profiles Astra OS execution metrics and generates performance optimization recommendations.
    """

    def __init__(self, metrics_service: Optional[MetricsService] = None):
        self._metrics_service = metrics_service

    def calculate_percentiles(self, values: List[float]) -> Dict[str, float]:
        """
        Calculates P50 (median), P95, and P99 percentiles from a list of latencies.
        """
        if not values:
            return {"p50": 0.0, "p95": 0.0, "p99": 0.0, "avg": 0.0, "max": 0.0}

        sorted_vals = sorted(values)
        n = len(sorted_vals)

        def percentile(p: float) -> float:
            idx = math.ceil((p / 100.0) * n) - 1
            idx = max(0, min(idx, n - 1))
            return sorted_vals[idx]

        avg_val = sum(sorted_vals) / n
        return {
            "p50": round(percentile(50), 2),
            "p95": round(percentile(95), 2),
            "p99": round(percentile(99), 2),
            "avg": round(avg_val, 2),
            "max": round(sorted_vals[-1], 2),
            "count": n
        }

    def get_profiler_stats(self) -> Dict[str, Any]:
        """
        Calculates profiling statistics across all recorded latency histograms.
        """
        if not self._metrics_service:
            return {"histograms": {}, "recommendations": []}

        summary = self._metrics_service.get_summary()
        histograms = self._metrics_service._histograms

        percentiles_by_metric = {}
        for name, values in histograms.items():
            percentiles_by_metric[name] = self.calculate_percentiles(values)

        recommendations = self.generate_recommendations()

        return {
            "histograms": percentiles_by_metric,
            "counters": summary.get("counters", {}),
            "gauges": summary.get("gauges", {}),
            "recommendations": recommendations
        }

    def generate_recommendations(self) -> List[Dict[str, str]]:
        """
        Automatically analyzes system metrics and outputs concrete optimization recommendations.
        Detects:
        1. Slow vector/memory retrieval (> 500ms)
        2. High LLM latency (> 3000ms)
        3. Excessive retries (> 3)
        4. High token usage (> 4000 tokens)
        5. Slow browser tool latency (> 4000ms)
        """
        recommendations = []

        if not self._metrics_service:
            return recommendations

        summary = self._metrics_service.get_summary()
        counters = summary.get("counters", {})
        histograms = self._metrics_service._histograms

        # 1. Slow Memory / Vector Retrieval Recommendation
        memory_latencies = histograms.get("memory_retrieval_ms", [])
        if memory_latencies:
            p95_mem = self.calculate_percentiles(memory_latencies)["p95"]
            if p95_mem > 500.0:
                recommendations.append({
                    "category": "Memory & Search",
                    "severity": "MEDIUM",
                    "issue": f"Memory vector retrieval P95 latency is high ({p95_mem}ms > 500ms).",
                    "recommendation": "Enable HNSW index pre-warming or decrease vector similarity top_k candidate limit."
                })

        # 2. LLM Latency Recommendation
        llm_latencies = histograms.get("llm_latency_ms", [])
        if llm_latencies:
            p95_llm = self.calculate_percentiles(llm_latencies)["p95"]
            if p95_llm > 3000.0:
                recommendations.append({
                    "category": "LLM Core Engine",
                    "severity": "HIGH",
                    "issue": f"LLM response latency P95 is high ({p95_llm}ms > 3000ms).",
                    "recommendation": "Switch to streaming output or utilize a smaller quantized model for simple reasoning steps."
                })

        # 3. Excessive Retries Recommendation
        total_retries = counters.get("operation_retries_total", 0.0)
        if total_retries > 3:
            recommendations.append({
                "category": "Execution Runtime",
                "severity": "HIGH",
                "issue": f"High operational retry count detected ({int(total_retries)} retries).",
                "recommendation": "Inspect tool timeout thresholds and check external API rate limit backoffs."
            })

        # 4. High Token Usage Recommendation
        total_tokens = counters.get("llm_total_tokens", 0.0)
        if total_tokens > 4000:
            recommendations.append({
                "category": "Cost & Performance",
                "severity": "MEDIUM",
                "issue": f"Excessive LLM token consumption detected ({int(total_tokens)} total tokens).",
                "recommendation": "Apply conversation context summarization before prompt injection to save tokens."
            })

        # 5. Browser Tool Latency
        browser_latencies = [
            v for k, vals in histograms.items() if "browser" in k.lower() for v in vals
        ]
        if browser_latencies:
            p95_browser = self.calculate_percentiles(browser_latencies)["p95"]
            if p95_browser > 4000.0:
                recommendations.append({
                    "category": "Browser Automation",
                    "severity": "MEDIUM",
                    "issue": f"Browser tool operation P95 latency is high ({p95_browser}ms > 4000ms).",
                    "recommendation": "Enable element caching or headless page navigation reuse."
                })

        return recommendations
