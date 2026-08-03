# ADR 008: Plugin SDK & Extension Platform Architecture

## Status
**Accepted** — 2026-07-31

## Context
As Project Astra OS evolves into an Extensible AI OS Platform, third-party developers require a clean SDK to extend Astra with custom tools, specialist agents, commands, and event subscribers without modifying Astra's core codebase.

However, loading third-party code presents security risks (unauthorized filesystem or network access) and stability concerns (crashing Astra runtime or duplicate tool registrations).

## Decision
We have designed and implemented the **Plugin SDK & Extension Platform** following Hexagonal Architecture:

1. **Clean Plugin Lifecycle Management**:
   - `BasePlugin` abstract class defines explicit lifecycle hooks (`on_load`, `register_tools`, `register_agents`, `on_unload`).
   - `PluginManager` handles discovery, manifest validation (`plugin.json`), sandboxing, loading, unloading, and hot reloading.

2. **Security & Permission Model**:
   - `PluginSandbox` enforces permission declarations (`network`, `filesystem`, `desktop`, `browser`, `email`, `microphone`).
   - Plugins cannot activate unless their requested permissions are approved by the user.

3. **Controlled SDK Surface API**:
   - `PluginAPI` provides controlled, safe gateways to Astra's `ToolRegistry`, `EventBus`, and logging system.

4. **Hot Reloading & Registry Isolation**:
   - Plugins can be dynamically reloaded (`hot_reload_plugin`) without restarting Astra OS.

## Consequences
- Developers can build third-party plugins (e.g. Spotify, Jira, GitHub) cleanly.
- Astra OS core code remains clean, stable, and decoupled.
