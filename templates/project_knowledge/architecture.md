# Architectural Foundations

## 1. High-Level System Overview
- **Application Type:** (monolith / microservice / CLI / library / plugin / extension)
- **Core Stack:** (language, framework, key libraries)

## 2. Key Components and Data Flows
- **Component 1:** Purpose, input, and output data.
- **Component 2:** Interaction with external APIs / database.
- **Data Flow:**
  `[Client/Input] -> [Validation Layer/API] -> [Business Logic] -> [Storage/Output]`

## 3. Data and State Invariants
- State management strategy (stateless / stateful / DB / local cache).
- Messaging format / interface contracts.

## 4. End-to-End Data Flows (Pre-Flight Flow Tracing)
Every multi-tier feature or bugfix touching client-server, UI, or storage boundaries must map the flow across components before making code changes:

```
[Origin: UI/CLI/Event] ➔ [Transport: API Route / Message] ➔ [Domain / Storage: Persistence] ➔ [Assembly / Packager] ➔ [Consumer: Client / Daemon]
```
- **Primary Data Flow 1:** [e.g. User Configuration ➔ Sync Route ➔ Atomic Store ➔ Client Polling]
- **Single Source of Truth:** [Specify authoritative owner of state]

## 5. Design Patterns
- Architectural patterns used (Clean Architecture, Ports & Adapters, MVC, CQRS, etc.).
- Error handling approach (Result type, exceptions, custom error classes).
