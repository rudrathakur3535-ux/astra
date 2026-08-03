# ADR 009: Observability & Developer Dashboard Subsystem

- **Status**: Accepted
- **Date**: 2026-08-01
- **Author**: Principal Observability Architect, Project Astra OS
- **Deciders**: Astra System Architecture Group

---

## Context and Problem Statement

As Project Astra OS scales into a multi-agent personal operating system (handling LLM reasoning, voice STT/TTS, headless browser automation, vector memory, desktop control, and plugin SDKs), simple file logging becomes insufficient. Developers and users need real-time visibility into active agent workflows, subsystem latencies, token consumption, error cascades, and state transitions.

We require a unified Observability & Developer Dashboard architecture that provides live metrics collection, distributed tracing with unique Trace IDs, central log aggregation, automated subsystem health monitoring, performance profiling, and real-time visualization.

---

## Decision Drivers

1. **System Visibility**: Ability to trace a multi-agent request from initial user voice/prompt input down to browser execution and vector retrieval.
2. **Hexagonal Decoupled Architecture**: Observability logic must interface via ports (`ObservabilityPort`) to remain independent of underlying storage or APM backends.
3. **Low Overhead**: Metrics recording and tracing must execute with sub-millisecond overhead.
4. **Real-time Developer Experience**: Provide both REST endpoints and WebSockets live streaming for web dashboards without full page reloads.
5. **Proactive Diagnostics**: Automated performance recommendations that pinpoint vector retrieval bottlenecks, excessive retries, or high LLM token usage.

---

## Key Concepts & Distinctions

### 1. Why Observability is Different from Logging
- **Logging**: Captures discrete, isolated events (`"User clicked search"`). Logs provide detailed textual context but lack structural aggregation or cross-subsystem correlation.
- **Observability**: The ability to infer the internal state of Astra OS by measuring its external outputs (metrics, spans, logs, health states). Observability provides actionable insight into *why* a workflow is failing or behaving slowly.

### 2. The Three Pillars of Observability
- **Metrics**: Numerical measurements aggregated over time (Counters for total tokens, Gauges for memory usage, Histograms for latency percentiles P50/P95/P99).
- **Traces**: Distributed execution trees linked by a unique `Trace ID` and parent-child `Span IDs`. Traces show exact execution order across agents, tools, and LLMs.
- **Logs**: Structured JSON records indexed by timestamp, log level, subsystem, and `Trace ID` for granular textual troubleshooting.

---

## Architectural Design

```
+-----------------------------------------------------------------------+
|                       Astra Developer Dashboard                       |
|                   (REST API & WebSockets /ws/dashboard)               |
+-----------------------------------------------------------------------+
                                   |
                                   v
+-----------------------------------------------------------------------+
|                          DashboardService                             |
+-----------------------------------------------------------------------+
    |               |               |             |               |
    v               v               v             v               v
MetricsService TraceManager LogAggregator HealthMonitor PerformanceProfiler
    |               |               |             |               |
    +---------------+---------------+-------------+---------------+
                                   |
                                   v
+-----------------------------------------------------------------------+
|                    ObservabilityPort (Interface)                      |
+-----------------------------------------------------------------------+
```

---

## Subsystem Architecture Details

1. **`MetricsService`**: Collects counters, gauges, and latency histograms. Includes helper methods for LLM latency, token usage, memory retrieval, tool latency, and high-latency alerts (> 2000ms threshold).
2. **`TraceManager`**: Manages `TraceSpan` objects, generates unique `Trace ID`s, tracks span hierarchies, and provides sync/async context managers (`span()` / `async_span()`).
3. **`LogAggregator`**: Ingests structured `LogEntry` records with filtering capabilities by level, subsystem, trace ID, and search query.
4. **`HealthMonitor`**: Continuously checks the 8 core Astra subsystems (`Voice`, `Knowledge`, `Memory`, `Plugin SDK`, `Browser`, `Communication`, `Execution Runtime`, `Core LLM`) and handles missing components gracefully.
5. **`PerformanceProfiler`**: Calculates P50, P95, and P99 latency percentiles and generates automated recommendations for memory index pre-warming, context summarization, or timeout adjustments.
6. **`WorkflowVisualizer`**: Renders node-and-edge Directed Acyclic Graphs (DAGs) for workflow visualization and active agent interactions.
7. **`DashboardAPI`**: FastAPI router serving JSON endpoints and WebSockets live streams at `http://localhost:8000/dashboard`.

---

## Future OpenTelemetry & Production Monitoring Roadmap

To transition to enterprise production environments:
1. **OpenTelemetry Exporter**: Implement an OTel exporter adapter adhering to `ObservabilityPort` to stream traces and metrics directly to Prometheus, Jaeger, Datadog, or Grafana Tempo.
2. **OTel Context Propagation**: Adopt W3C Trace Context headers (`traceparent`) for cross-process tracing when running distributed worker nodes.
3. **Production Guardrails**: Rate-limit WebSocket connections and compress historical log buffers.

---

## Verification & Test Strategy

Unit tests in `tests/test_observability.py` cover:
- Metric recording and histogram calculations.
- Trace span generation and hierarchy.
- Subsystem health checks and missing subsystem handling.
- Timeline chronological ordering.
- Dashboard API REST endpoints and WebSockets router.
- Log aggregation and filtering.
- Workflow visualization DAG creation.
- Performance profiler percentiles and optimization recommendations.
