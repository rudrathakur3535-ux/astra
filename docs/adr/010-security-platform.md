# ADR 010: Security, Identity & Secret Management Platform

- **Status**: Accepted
- **Date**: 2026-08-01
- **Author**: Principal Security Architect, Project Astra OS
- **Deciders**: Astra System Architecture Group

---

## Context and Problem Statement

Project Astra OS executes operating system commands, automated browser sessions, code modifications, and external communications (email, WhatsApp). Leaving credentials scattered in plain-text `.env` files or allowing unauthenticated/unauthorized tool calls presents significant security risks.

We require a comprehensive Security, Identity & Secret Management Platform that enforces Zero-Trust principles, role-based access control (RBAC), secret isolation, encrypted credential storage, policy enforcement with user confirmation prompts, and immutable security audit trails.

---

## Decision Drivers

1. **Zero-Trust Access Control**: Every operation (whether triggered by user voice, multi-agent planner, or plugin) must pass through identity resolution, authorization check, and policy evaluation.
2. **Secret Isolation**: System components and LLM prompts must never access raw `.env` keys directly. Secrets must pass through `SecretManager` with masking support.
3. **Immutable Audit Trail**: All sensitive actions (file deletion, terminal execution, process termination) must produce SHA-256 signed audit records.
4. **Hexagonal Architecture**: Security services must interface via ports (`SecurityPort`) to allow swapping local credential stores with Windows Credential Manager or cloud vaults.

---

## Key Principles & Architectural Concepts

### 1. Authentication vs. Authorization
- **Authentication ("Who are you?")**: Managed by `AuthenticationEngine` & `SessionManager`. Verifies credentials (passwords, API keys, session tokens) and resolves a valid `UserIdentity`.
- **Authorization ("What are you allowed to do?")**: Managed by `AuthorizationEngine` & `PolicyEngine`. Evaluates `UserRole` (`OWNER`, `ADMIN`, `STANDARD_USER`, `GUEST`) and `ResourceScope` to permit or deny actions.

### 2. Secret Management Strategy
- Raw API keys (e.g., `OPENAI_API_KEY`, `ELEVENLABS_API_KEY`) are stored in `CredentialStore` using base64 obfuscation/local encryption.
- `SecretManager` provides masked outputs (e.g., `sk-***5678`) for logging and UI displays, eliminating accidental API key leaks in logs.

### 3. Immutable Security Audit Trail
- Every sensitive operation generates an `AuditRecord` containing:
  - `audit_id`, `timestamp`, `user_id`, `workflow_id`, `action`, `tool_name`, `resource`, `result`, and `parameters`.
  - SHA-256 cryptographic signature (`signature`) verifying tamper resistance.

### 4. Policy Engine Guardrails
```
Operation Request

↓

Authentication & Identity Resolution

↓

RBAC Authorization Check

↓

Policy Engine Confirmation Check (if High-Risk)

↓

Immutable Audit Trail Logging

↓

Tool Execution
```

---

## Future Enterprise Vault Roadmap

1. **Windows Credential Manager / macOS Keychain Integration**: Replace base64 obfuscation in `CredentialStore` with native OS keychains via `ctypes`/`pywin32`.
2. **HashiCorp Vault / AWS Secrets Manager Adapter**: Implement an enterprise `SecurityPort` adapter for dynamic secret rotation and centralized RBAC.
3. **Hardware Token / Passkey Support**: Support FIDO2 WebAuthn / YubiKey hardware tokens for high-privilege `OWNER` confirmations.

---

## Verification & Test Strategy

Unit tests in `tests/test_security.py` cover:
- Authentication flow & credential matching.
- Session creation, validation, expiration, and revocation.
- Role-based authorization evaluation (`OWNER`, `ADMIN`, `STANDARD_USER`, `GUEST`).
- Secret management storage, retrieval, and masking.
- Policy engine confirmation requirements & denial enforcement.
- SHA-256 audit record signature generation and integrity verification.
