# ADR 011: Desktop Application Architecture (Electron + React)

- **Status**: Accepted
- **Date**: 2026-08-01
- **Author**: Principal Desktop Architect, Project Astra OS
- **Deciders**: Astra System Architecture Group

---

## Context and Problem Statement

Up to Day 15, Project Astra OS operated primarily via terminal CLI and REST endpoints. To transform Astra into a personal AI Operating System that users can install, run daily, and interact with seamlessly, we require a desktop application interface.

We require a desktop architecture that combines native OS window management, real-time voice controls, interactive multi-agent workspace visualization, and secure IPC bridging to the Python backend runtime.

---

## Decision Drivers

1. **User Experience**: A 3-pane desktop application (Sidebar, Conversation Canvas, Agent & Memory Inspector, Voice Bar) providing immediate visual feedback during multi-agent workflows.
2. **Security & Context Isolation**: Electron Main process must enforce strict `contextIsolation: true` and `sandbox: true`, exposing only sanitized IPC channels via `preload.js` (`window.astraAPI`).
3. **Dynamic Settings & Plugin Management**: Users must be able to change AI providers, voice engines, wake words, and plugin permissions without editing `.env` files manually.
4. **Decoupled Client-Server Bridge**: The Electron/React frontend communicates with the Python backend over REST (`/api/*`) and WebSockets (`/ws/*`), enabling remote desktop deployment scenarios in the future.

---

## Architecture Diagram

```
+-----------------------------------------------------------------------+
|                    Electron Main Process (main.js)                    |
+-----------------------------------------------------------------------+
                                   |
                          Context Bridge IPC
                                   v
+-----------------------------------------------------------------------+
|                 React Renderer Process (desktop/src/)                  |
| ┌──────────────┬───────────────────────────────┬────────────────────┐ |
| │ Left Sidebar │     Center Chat Canvas        │  Right Agent       │ |
| │  Navigation  │   (Prompt Feed & Workflows)   │  Inspector         │ |
| └──────────────┴───────────────────────────────┴────────────────────┘ |
| └────────────────────── Bottom Voice Control Bar ──────────────────┘ |
+-----------------------------------------------------------------------+
                                   |
                         REST & WebSockets Bridge
                                   v
+-----------------------------------------------------------------------+
|                   FastAPI Backend Runtime (app/api/)                  |
|                     (/api/chat, /api/settings, etc)                   |
+-----------------------------------------------------------------------+
```

---

## Component Responsibilities

1. **`main.js` & `preload.js`**: Electron main launcher managing native windows, IPC handlers, and context-isolated APIs.
2. **React Shell (`App.jsx`)**: Responsive 3-pane layout containing Sidebar, ChatCanvas, AgentInspector, VoiceControlBar, PluginManagerUI, and SettingsUI.
3. **`SettingsService`**: Provides persistent configuration management for AI providers, voice parameters, wake words, and plugin permissions.
4. **`DesktopBridge`**: Event aggregator dispatching voice status updates, agent topology changes, and UI events.
5. **`FastAPI Application API` (`app/api/app_api.py`)**: REST endpoints serving chat prompt execution, settings updates, plugin management, and voice controls.

---

## Packaging & Distribution Strategy

- **Electron Builder**: Package desktop apps for Windows (`.exe` / `.msi`), macOS (`.dmg`), and Linux (`.AppImage`).
- **Python Runtime Bundling**: Bundle Python backend dependencies or PyInstaller executable alongside Electron assets for one-click installation.

---

## Verification & Test Strategy

Unit and integration tests in `tests/test_desktop_app.py` cover:
- FastAPI Application API endpoints (`/api/chat`, `/api/agents/active`, `/api/settings`, `/api/plugins`, `/api/voice/status`).
- `SettingsService` JSON persistence and dynamic updates.
- `DesktopBridge` event listeners and voice state toggling.
