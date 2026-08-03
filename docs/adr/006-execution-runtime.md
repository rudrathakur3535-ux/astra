# ADR 006: Autonomous Execution Runtime Architecture

## Status
**Accepted** — 2026-07-31

## Context
As Project Astra OS transitions to Phase 2/3 (Autonomous Execution Intelligence), long multi-agent workflows require resilient runtime execution capabilities. 

If a multi-step task experiences a power loss, network hang, or system restart midway through, Astra must not lose progress or repeat completed steps. It requires state persistence, step-by-step checkpointing, configurable retry strategies, timeout guardrails, and progress tracking.

## Decision
We have designed and implemented the **Autonomous Execution Runtime** following Hexagonal Architecture:

1. **Separation of Execution Runtime from Planning**:
   - `PlannerAgent` and `ManagerAgent` construct DAG workflows.
   - `ExecutionRuntime` handles long-running execution, thread safety, state persistence, and worker management.

2. **Persistent Checkpointing & Crash Recovery**:
   - `CheckpointManager` and `StateStore` (SQLite database) save immutable execution checkpoints (`ExecutionCheckpoint`) after every step.
   - Upon restart, `ExecutionRuntime` detects prior state and resumes execution from the exact step index where it was interrupted.

3. **Configurable Retry Policies & Timeout Guardrails**:
   - `RetryPolicy` provides configurable retry backoffs (`EXPONENTIAL_BACKOFF`, `FIXED_DELAY`, `IMMEDIATE`).
   - `TimeoutManager` wraps async agent tasks in `asyncio.wait_for` to cancel hanging operations safely (e.g. browser searches hanging >60s).

4. **Live Progress Tracking & Metrics**:
   - `ProgressTracker` renders visual progress bars (e.g. `[████████░░] 80%`).
   - `ExecutionMonitor` collects metrics (active workflows, step latency, success rates, retry counts).

## Consequences
- Long multi-agent workflows execute autonomously and reliably over extended timeframes.
- System crashes or restarts do not cause data loss or duplicate step executions.
