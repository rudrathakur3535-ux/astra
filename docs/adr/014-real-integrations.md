# ADR 014: Real Integrations & AI Workspace Platform

- **Status**: Accepted
- **Date**: 2026-08-01
- **Author**: Principal Integration & Developer Experience Architect, Project Astra OS
- **Deciders**: Astra System Architecture Group

---

## Context and Problem Statement

To transition Project Astra OS from an engineering infrastructure platform into a real digital co-worker, Astra must interact with real-world developer tools (GitHub, Gmail, Google Calendar, Notion, VS Code Workspaces).

We require an Integration & AI Workspace Platform that securely handles Google & GitHub OAuth tokens via `SecretManager`, indexes repository diffs, drafts email replies, detects calendar schedule conflicts, manages Notion notes, and maps VS Code project dependency graphs.

---

## Decision Drivers

1. **Secure OAuth Token Isolation**: All integration access tokens (GitHub Personal Access Tokens, Google OAuth, Notion API keys) are stored and retrieved via `SecretManager` and `CredentialStore`.
2. **Hexagonal Integration Abstraction**: Service adapters adhere to `IntegrationPort` to isolate API changes from the core agent runtime.
3. **Workspace Intelligence**: Deep project awareness linking open VS Code editor tabs, git commit history, and AST module dependency graphs.
4. **Smart Engineering Briefings**: Daily aggregation summarizing open GitHub PRs, unread emails, upcoming meetings, and suggested priorities.

---

## Architecture Diagram

```
+-----------------------------------------------------------------------+
|                    Master IntegrationService                          |
+-----------------------------------------------------------------------+
    |                |                 |               |               |
    v                v                 v               v               v
GitHubService   GmailService    CalendarService  NotionService WorkspaceService
    |                |                 |               |               |
    +----------------+-----------------+---------------+---------------+
                                       |
                                       v
                          SecretManager (OAuth Tokens)
                                       |
                                       v
                             PolicyEngine & AuditLogger
```

---

## Component Specifications

1. **`GitHubService`**: PR code reviewer (`PullRequestService`), repo indexer (`RepositoryManager`), and issue summarizer (`IssueService`).
2. **`GmailService`**: Thread indexer & priority detector (`MailIndexer`), inbox search, and draft generator (`GmailOAuthManager`).
3. **`CalendarService`**: Conflict detector & free slot finder (`AvailabilityEngine`).
4. **`NotionService`**: Workspace indexer (`NotionWorkspaceIndexer`) and page search/creation engine.
5. **`WorkspaceService`**: VS Code tab inspector (`VSCodeBridge`), AST dependency mapper (`WorkspaceIndexer`), and project context builder (`ProjectContextBuilder`).
6. **`IntegrationService`**: Master orchestrator generating Smart Daily Briefings.

---

## Verification & Test Strategy

Unit and integration tests in `tests/test_integrations.py` cover:
- GitHub PR code review diff analysis.
- Gmail inbox search, thread summarization, and draft creation.
- Calendar scheduling & conflict detection.
- Notion workspace page search and creation.
- VS Code workspace AST dependency graph generation.
- Smart Daily Briefing payload generation.
- FastAPI REST endpoints (`/api/integrations/daily-brief`, `/github/review`, `/gmail/draft`, `/calendar/schedule`, `/workspace/context`).
