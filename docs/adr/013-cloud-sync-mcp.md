# ADR 013: Cloud Sync, Local AI & Model Context Protocol (MCP) Platform

- **Status**: Accepted
- **Date**: 2026-08-01
- **Author**: Chief Distributed Systems & AI Platform Architect, Project Astra OS
- **Deciders**: Astra System Architecture Group

---

## Context and Problem Statement

Project Astra OS must transition from a single-device desktop application into a distributed, hybrid AI operating system. It must operate seamlessly both online (leveraging OpenAI, Gemini, OpenRouter) and offline (using local Ollama models), sync chats, memory, knowledge, settings, plugins, and workflows across multi-device clusters (laptops, desktops, mobile), resolve data conflicts, and interface with external standard tools via the Model Context Protocol (MCP).

---

## Decision Drivers

1. **Hybrid AI Engine**: Support seamless execution across local LLMs (Ollama) and cloud LLMs (OpenAI, Gemini, OpenRouter) with automatic failover if internet or cloud APIs fail.
2. **Privacy & Offline First**: Provide zero-telemetry local execution for sensitive tasks and offline environments.
3. **Multi-Device Sync & Resilient Queueing**: Enqueue delta updates locally when offline (`OfflineQueue`) and automatically flush updates upon network reconnection.
4. **Data Conflict Resolution**: Resolve multi-device state collisions using configurable `LATEST_WINS`, `MERGE`, and `MANUAL` conflict strategies.
5. **Standardized Extensibility via MCP**: Adopt the Model Context Protocol (MCP) to interact with external tools (GitHub, Notion, Google Drive, Filesystem, Database) using standard JSON-RPC RPC calls.

---

## Architecture Diagram

```
+-----------------------------------------------------------------------+
|                            ASTRA OS UI                                |
+-----------------------------------------------------------------------+
                                   |
                  +----------------+----------------+
                  |                                 |
                  v                                 v
     ProviderRouter & Selector              SyncManager & Registry
     (OpenAI/Gemini/Ollama)                 (Multi-Device Cluster)
                  |                                 |
                  +----------------+----------------+
                                   |
                                   v
                         MCP Client & Router
                     (Standardized JSON-RPC)
                                   |
        +---------------+----------+----------+---------------+
        |               |                     |               |
   GitHub MCP       Notion MCP          Filesystem MCP    Drive MCP
```

---

## Subsystem Architecture Details

1. **`ProviderRouter` & `ProviderSelector`**: Dispatches prompts across providers and automatically selects the optimal provider based on connectivity, privacy policies, and task types (e.g., fast answers -> Gemini, deep reasoning -> OpenAI, offline/sensitive -> Ollama).
2. **`OllamaAdapter`**: Implements `ProviderPort` for local LLM inference and 384-dimensional vector embedding generation.
3. **`SyncManager` & `SyncService`**: Tracks registered cluster nodes (`DeviceNode`) and emits delta `SyncEvent` payloads.
4. **`OfflineQueue` & `ConflictResolver`**: Buffers sync updates during network loss and handles state reconciliation.
5. **`MCPClient`, `MCPServer`, `MCPRegistry`, `MCPRouter`**: Client/Server infrastructure managing MCP tool registration and JSON-RPC execution.

---

## Security & Encryption Roadmap

1. **End-to-End Encryption (E2EE)**: Encrypt delta sync payloads before sending over sync channels.
2. **Local Vector Embeddings**: Generate embeddings locally via Ollama to reduce cloud API token costs and data exposure.
3. **MCP Tool Authorization**: Pass all external MCP tool executions through the Astra Policy Engine and Security Audit Logger.

---

## Verification & Test Strategy

Unit and integration tests in `tests/test_sync_mcp.py` cover:
- Provider routing & automatic failover.
- Ollama local adapter execution & embedding generation.
- Sync manager push/pull operations & offline queue flushing.
- Conflict resolution strategies (`LATEST_WINS`, `MERGE`).
- Device registration & cluster node management.
- MCP client connection, resource discovery, and tool call routing.
- FastAPI REST endpoints (`/api/sync/push`, `/api/devices`, `/api/providers/status`, `/api/mcp/call`).
