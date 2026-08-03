# ADR 012: Deployment, Packaging & Distribution Platform

- **Status**: Accepted
- **Date**: 2026-08-01
- **Author**: Principal Deployment Architect, Project Astra OS
- **Deciders**: Astra System Architecture Group

---

## Context and Problem Statement

To transform Project Astra OS from a complex engineering repository into a production-grade product usable by non-technical end users, Astra must be deployable and installable in under 5 minutes without manual terminal setup or editing `.env` files.

We require a unified Deployment, Packaging & Distribution Platform that provides automated setup wizards, version checking & auto-updating, exportable diagnostic bundles, crash reporting, cross-platform installer packages (Windows, macOS, Linux), and Docker containerization.

---

## Decision Drivers

1. **User Onboarding (Under 5 Mins)**: Non-technical users must be able to launch Astra, enter API keys in an Onboarding Setup Wizard, and begin using the AI OS immediately.
2. **Auto-Updater Security**: Updates must be validated against version manifests (`DeploymentManifest`) and checksums before applying hot-patches.
3. **Troubleshooting & Diagnostics**: Systems must bundle hardware specs, metrics, active Trace IDs, health reports, and crash logs into a single downloadable diagnostic archive.
4. **Cross-Platform Installer Packaging**: Electron Builder configurations (`builder-config.json`) supporting Windows (`.exe` NSIS / `.msi`), macOS (`.dmg`), and Linux (`.AppImage`).
5. **Docker Backend Containerization**: Multi-stage `Dockerfile` and `docker-compose.yml` orchestrating FastAPI backend, ChromaDB vector store, and SQLite persistence.

---

## Architecture Diagram

```
+-----------------------------------------------------------------------+
|                      Installer Packages & Releases                    |
|          Windows (.exe/MSI)  |  macOS (.dmg)  |  Linux (.AppImage)    |
+-----------------------------------------------------------------------+
                                   |
                                   v
+-----------------------------------------------------------------------+
|                       Setup Wizard Engine                             |
|          (API Keys -> SecretManager -> SettingsService)               |
+-----------------------------------------------------------------------+
                                   |
                                   v
+-----------------------------------------------------------------------+
|               FastAPI Deployment API (/api/deployment/*)               |
|      (/status, /setup, /update, /diagnostics, /crash-report)          |
+-----------------------------------------------------------------------+
    |                 |                   |                   |
    v                 v                   v                   v
AutoUpdater   DiagnosticBundler     CrashReporter      PackagerService
```

---

## Component Specifications

1. **`SetupWizard`**: Handles first-time setup configuration, API key ingestion, and `SecretManager` secret masking.
2. **`AutoUpdater`**: Parses semver version strings, evaluates release manifests, and triggers hot-patch updates.
3. **`DiagnosticBundler`**: Collects system hardware specs (RAM, CPU, OS release via `psutil`), subsystem health reports, recent logs, and active trace IDs.
4. **`CrashReporter`**: Captures uncaught runtime exceptions, formats stack traces, attaches current `Trace ID`, and logs crash reports.
5. **`PackagerService`**: Evaluates platform build specs for Windows, macOS, and Linux targets.
6. **Docker & Compose Artifacts**: Production `Dockerfile` and `docker-compose.yml` for isolated container deployments.

---

## Verification & Test Strategy

Unit and integration tests in `tests/test_deployment.py` cover:
- Setup Wizard secret ingestion & completion flag persistence.
- Auto-Updater version parsing, manifest comparison, and update triggers.
- Diagnostic Bundler hardware specs & report payload generation.
- Crash Reporter exception stack trace formatting & trace correlation.
- Packager Service build spec evaluation.
- FastAPI Deployment API REST endpoints (`/status`, `/setup`, `/update`, `/diagnostics`, `/crash-report`).
