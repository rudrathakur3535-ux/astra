# ADR 015: Performance, Reliability & Production Readiness Platform

- **Status**: Accepted
- **Date**: 2026-08-01
- **Author**: Principal Performance & Reliability Architect, Project Astra OS
- **Deciders**: Astra System Architecture Group

---

## Context and Problem Statement

Project Astra OS has completed feature development across all major subsystem layers (Multi-Agent Runtime, Knowledge, Memory, Desktop, Browser, Observability, Cloud Sync, MCP, and Real Integrations).

To transition Astra OS into a production-grade software platform that operates reliably for long-running sessions, handles peak concurrent loads, and gracefully recovers from external service failures, we require a dedicated Performance, Reliability & Production Readiness Subsystem.

---

## Decision Drivers

1. **Comprehensive Benchmarking**: Measure execution latencies across agents, tools, memory, RAG, providers, and multi-agent workflows with statistical P50, P95, and P99 percentiles.
2. **Multi-Tier LRU Caching**: Eliminate redundant API calls and vector computations via LRU caching for prompt responses, embeddings, tool outputs, and session states.
3. **Resilient Circuit Breakers**: Implement the Circuit Breaker pattern (`CLOSED`, `OPEN`, `HALF_OPEN`) to isolate upstream provider failures (OpenAI, Gemini, OpenRouter) and seamlessly trigger local Ollama failover.
4. **Real-Time Resource Monitoring**: Harvest CPU %, RAM %, Disk %, active thread counts, and queue depth.
5. **State Checkpointing & Graceful Recovery**: Save runtime checkpoints to disk and auto-restore active states after crashes or orderly shutdowns.

---

## Architecture Diagram

```
+-----------------------------------------------------------------------+
|                    Master PerformanceService                          |
+-----------------------------------------------------------------------+
    |                |                 |               |               |
    v                v                 v               v               v
BenchmarkRunner   CacheManager  CircuitBreakers ResourceMonitor  HealthRecovery
(P50/P95/P99)      (LRU Cache)   (CLOSED/OPEN)     (CPU/RAM)        (Checkpoint)
    |                |                 |               |               |
    +----------------+-----------------+---------------+---------------+
                                       |
                                       v
                           GracefulShutdownManager
```

---

## Component Specifications

1. **`BenchmarkRunner` & `LatencyAnalyzer`**: Executes benchmark iterations and computes statistical percentiles.
2. **`CacheManager`**: Multi-level LRU cache (`LRUCache`) for prompts (200 slots), embeddings (500 slots), tool results (100 slots), and sessions (50 slots).
3. **`CircuitBreaker`**: State machine (`CLOSED`, `OPEN`, `HALF_OPEN`) with configurable failure threshold (default 3) and recovery timeout (default 5s).
4. **`ResourceMonitor`**: System harvester collecting hardware metrics via `psutil` and `threading`.
5. **`LoadTester`**: Concurrency test utility using `ThreadPoolExecutor` to stress test multi-agent workflows.
6. **`HealthRecoveryEngine` & `GracefulShutdownManager`**: Disk state persistence (`runtime_checkpoint.json`) and clean application shutdown hook executor.

---

## Verification & Test Strategy

Unit and integration tests in `tests/test_performance_reliability.py` cover:
- Benchmark execution & P50/P95/P99 percentile calculation.
- LRU cache hits, misses, evictions, and clear operations.
- Resource monitor hardware snapshot harvesting.
- Circuit breaker state transitions (`CLOSED` -> `OPEN` -> `HALF_OPEN`).
- Token bucket rate limiter token acquisition & throttling.
- Graceful shutdown hook execution and checkpoint recovery.
- Load tester concurrent task execution.
- FastAPI REST endpoints (`/api/performance/report`, `/performance/resources`, `/performance/load-test`, `/performance/cache`, `/reliability/circuit-breakers`).
