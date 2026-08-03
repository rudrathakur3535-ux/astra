# ADR 016: Adaptive Intelligence & Learning Engine Platform

- **Status**: Accepted
- **Date**: 2026-08-01
- **Author**: Principal AI Learning Systems Architect, Project Astra OS
- **Deciders**: Astra System Architecture Group

---

## Context and Problem Statement

Project Astra OS has completed feature development, deployment infrastructure, real-world integrations, and production readiness controls. To transition Astra from an execution runtime into a self-improving digital co-worker, the platform must learn developer habits, adapt to preferences over time, build a Personal Knowledge Graph connecting developer entities, and optimize prompt execution dynamically while respecting user privacy.

---

## Decision Drivers

1. **Habit Detection & Pattern Mining**: Automatically detect recurring multi-step user interaction routines and contextual triggers (e.g. morning workspace setup).
2. **Preference Learning**: Adaptively tune default AI LLM providers, themes, tool behaviors, and editor configurations without hardcoded settings.
3. **Personal Knowledge Graph**: Represent developer entity relationships (`KnowledgeNode`, `KnowledgeEdge`) connecting projects, skills, goals, preferences, and memories.
4. **Proactive Workflow Recommendations**: Suggest automated workflow templates when high-confidence habit patterns are detected.
5. **Zero-Telemetry Privacy Controls**: Provide complete transparency, allowing users to inspect, delete specific habits, or perform full learning data resets (`/api/learning/reset`).

---

## Architecture Diagram

```
+-----------------------------------------------------------------------+
|                       Master LearningService                          |
+-----------------------------------------------------------------------+
    |                |                 |               |               |
    v                v                 v               v               v
HabitDetector   PreferenceEngine  KnowledgeGraph RecEngine   FeedbackAnalyzer
(Routine Miner)  (Adaptive Config) (Nodes & Edges)(Proactive) (Corrections)
    |                |                 |               |               |
    +----------------+-----------------+---------------+---------------+
                                       |
                                       v
                          Privacy Deletion & Reset Endpoint
```

---

## Component Specifications

1. **`HabitDetector` & `PatternMiner`**: Mines interaction logs for recurring sequence patterns (`Habit`) and contextual triggers (`Pattern`).
2. **`PreferenceEngine`**: Dynamic key-value store learning provider, tool, and theme preferences.
3. **`WorkflowLearner`**: Converts high-confidence habits into executable workflow templates (`learn_workflow_from_habit`).
4. **`PersonalKnowledgeGraph`**: Graph manager maintaining developer nodes (`user`, `project`, `skill`, `goal`) and weighted relation edges.
5. **`RecommendationEngine`**: Ranks proactive suggestions (`Recommendation`) for user acceptance.
6. **`FeedbackAnalyzer`**: Analyzes explicit user correction signals and tunes preference settings.

---

## Verification & Test Strategy

Unit and integration tests in `tests/test_learning.py` cover:
- Habit detection from action sequence logs.
- Interaction pattern mining & time window tracking.
- Preference updates and retrieval.
- Personal Knowledge Graph node/edge creation and summary generation.
- Proactive recommendation generation and acceptance lifecycle.
- Automated workflow creation from learned habits.
- Feedback signal processing & prompt optimization.
- Privacy compliance: single habit deletion and full learning reset.
- FastAPI REST endpoints (`/api/learning/habits`, `/preferences`, `/recommendations`, `/knowledge-graph`, `/reset`).
