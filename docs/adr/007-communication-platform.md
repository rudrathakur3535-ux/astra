# ADR 007: Communication & Productivity Platform Architecture

## Status
**Accepted** — 2026-07-31

## Context
As Project Astra OS enters Day 12 (Communication & Productivity Platform), Astra must interface with external productivity tools (Email, Calendar, Desktop Notifications, Contacts) to become an AI engineering productivity partner.

However, external dispatches (sending emails, altering calendar invites, broadcasting messages) present security risks and automation policy constraints (e.g. rate limits or API permissions).

## Decision
We have designed and implemented the **Communication & Productivity Platform** following Hexagonal Architecture:

1. **Provider Abstraction through Ports and Adapters**:
   - `CommunicationPort` defines standard interfaces for Email, Calendar, Notifications, and Contacts.
   - `GmailAdapter`, `CalendarAdapter`, and `NotificationAdapter` isolate provider specifics from core business logic, allowing effortless swapping of underlying APIs (e.g. switching from Gmail SMTP to Outlook Graph API).

2. **Mandatory Security & Permission Layer Enforcement**:
   - All outgoing email dispatches and external messages pass through `MessageRouter` and Astra's `PermissionLayer`.
   - Actions with external side-effects require explicit user approval (`PermissionLevel.REQUIRES_APPROVAL`) before execution.

3. **Conflict Detection & Daily Briefings**:
   - `CalendarService` evaluates overlapping event windows (`is_overlapping_with`) to prevent double-booking.
   - `CommunicationService` consolidates schedule events, unread priority emails, and notifications into a single morning Daily Briefing.

## Consequences
- Astra can seamlessly manage email drafts, calendar schedules, desktop toast notifications, and address books.
- External actions are 100% safe and permission-controlled.
