# ADR 003: Agent Planning & Verification Architecture

## Status
**Accepted** — 2026-07-31

## Context
As Project Astra evolves into an intelligent Personal AI OS (Phase 2), executing tool calls in a naive single-turn fashion (`User -> LLM -> Single Tool`) is insufficient for complex user goals (e.g. "Research LangGraph", "Create project FinanceAI", "Open YouTube and search for tutorials"). 

Complex intent requires multi-step decomposition, step dependency ordering, pre-execution safety validation, empirical outcome verification, and self-correction reflection.

## Decision
We have designed and implemented an in-house **Agentic Planning Engine** following Hexagonal Architecture:

1. **Separation of Planning and Execution**:
   - `PlannerAgent` translates high-level goals into structured `Plan` objects containing ordered `PlanStep`s.
   - `PlanValidator` inspects tool existence, schema matching, circular dependencies, and security permissions *before* any execution begins.
   - `ExecutorAgent` drives step-by-step execution strictly through the central `ToolRouter` and `PermissionLayer`.

2. **Empirical Verification Agent**:
   - `VerificationAgent` independently verifies physical real-world state (checking running processes via `psutil`, window states via `pygetwindow`, filesystem existence via `os.path`) instead of blindly trusting tool output status strings.

3. **Reflection & Self-Correction Agent**:
   - `ReflectionAgent` evaluates overall goal completion post-execution.
   - Triggers step retries and fallback tool execution (self-correction) on recoverable failures.
   - Stores successful plan sequences in `PlanCache` to instantly reuse plan steps for recurring goals.

## Trade-offs: Custom Planning Engine vs Frameworks (e.g., LangGraph)

| Dimension | Custom Agent Planning Engine (Day 7) | LangGraph / AutoGen Frameworks |
|---|---|---|
| **Architectural Clarity** | 100% control over state machine, DAG dependency resolution, and custom tool router security. | Abstraction layer hides graph state mechanics under framework conventions. |
| **Verification & Security** | Direct integration with Astra's `PermissionLayer` and empirical system verification. | Requires custom state node wrappers around framework edges. |
| **Performance & Latency** | Zero extra framework overhead; lightweight `PlanCache` for instant recurring goal execution. | Extra graph state serialization and context overhead. |
| **Future Extensibility** | Easy migration path to LangGraph state graphs in Phase 3 because core agent roles (Planner, Executor, Verifier, Reflector) are already decoupled. | N/A |

## Consequences
- All high-level agent goals will route through `PlannerAgent -> PlanValidator -> ExecutorAgent -> VerificationAgent -> ReflectionAgent`.
- Safety and security are guaranteed because execution is constrained by `PlanValidator` and `ToolRouter` permission checks.
