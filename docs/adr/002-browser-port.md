# ADR 002: Browser Subsystem Hexagonal Ports & Adapters Architecture

* **Status**: Accepted
* **Date**: 2026-07-31
* **Authors**: Project Astra AI OS Engineering Team

---

## Context & Problem Statement

Project Astra requires deep web browsing, domain searching, multi-tab manipulation, and page reading capabilities. Directly coupling higher-level business services (such as `ChatService` or LLM Agent orchestrators) to a specific browser automation framework (e.g. raw Playwright, Selenium, or Puppeteer API) creates tight coupling. 

If Playwright introduces breaking API changes or if the system needs to switch to a cloud-hosted browser cluster (e.g. Browserless.io) or Selenium adapter in the future, refactoring would affect the entire application.

---

## Decision Drivers

1. **Hexagonal Architecture Compliance**: Application services must depend only on abstract interface contracts (`BrowserPort`), not framework implementation details.
2. **Persistent Session State**: Avoid launching a cold browser process for every command; maintain persistent context, history, and active tabs across user queries.
3. **Framework Swapability**: Enable replacing Playwright with Selenium, Puppeteer, or Cloud CDP drivers without modifying a single line of tool router or ChatService logic.
4. **Context-Aware Web Reader**: Extract cleaned Markdown DOM text for LLM/Voice processing without sending heavy raw HTML markup to the model.

---

## Considered Options

1. **Direct Playwright Integration in Tools**: Simple to implement initially, but tightly couples all 13 browser tools to Playwright's sync/async API.
2. **Selenium WebDriver Adapter**: Mature ecosystem, but slower startup times and heavier memory footprint.
3. **Hexagonal Ports & Adapters (`BrowserPort` + `PlaywrightAdapter`)**: Abstracts browser actions behind a clean, framework-agnostic port interface.

---

## Decision Outcome

**Chosen Option**: **Option 3 - Hexagonal Ports & Adapters Architecture**

* **`app/ports/browser_port.py`**: Defines abstract operations (`open_url`, `google_search`, `youtube_search`, `github_search`, `current_page`, `page_title`, `read_page`, `new_tab`, `close_tab`, `switch_tab`, `refresh`, `back`, `forward`, `close`).
* **`app/adapters/playwright_adapter.py`**: Implements `BrowserPort` using Playwright Chromium with persistent session management, automatic tab tracking, and crash recovery.
* **`app/browser/web_reader.py`**: Intelligent DOM parser extracting clean Markdown text for LLMs and TTS voice generation.

---

## Consequences & Trade-Offs

### Positive
* **Decoupled Architecture**: `ChatService` and `ToolRouter` depend exclusively on `BrowserPort`.
* **Zero Playwright Leakage**: No Playwright objects or exceptions leak outside `PlaywrightAdapter`.
* **Persistent Performance**: Browser session remains open across queries, minimizing startup latency.

### Negative / Mitigations
* **Single Thread Concurrency**: Playwright sync API requires thread synchronization when called across background worker threads. Handled cleanly with internal locks and thread-safe session managers.
