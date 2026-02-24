# System Overview & Architecture

This document provides a high-level view of the entire ecosystem, visualizing how the separate components (`Cloud Bot Controller`, `Script Spese`, `Personal Vision Services`) interact.

> **IMPORTANT**: Always update this document and the Mermaid diagrams below when architectural changes occur.

## 🌍 The "Hub-and-Spoke" Architecture

The system is composed of three distinct Google Cloud Projects (GCP) interacting via strict protocols.

```mermaid
graph TD
    User((User))
    
    subgraph "GCP: bot-orchestrator-hub"
        Hub[Bot Controller<br/>(Cloud Run / Python)]
        Secret[Secret Manager]
    end
    
    subgraph "GCP: YOUR_GCP_PROJECT_ID"
        AI_API[Gemini AI<br/>(API Provider)]
        Vision_API[Cloud Vision<br/>(API Provider)]
    end
    
    subgraph "Google Workspace"
        Spoke[Script Spese<br/>(Apps Script / TS)]
        Sheet[Google Sheets]
        Drive[Google Drive]
    end
    
    User -->|Telegram| Hub
    Hub -->|JSON Protocol| Spoke
    Spoke -->|Read/Write| Sheet
    Spoke -->|Read/Write| Drive
    
    %% AI interaction via Hub proxy
    Spoke -.->|Request AI| Hub
    Hub -.->|Proxy Request| AI_API
    Hub -.->|Proxy Request| Vision_API
    
    %% Secrets
    Secret -.->|Inject Secrets| Hub
```

## 🔄 End-to-End Flows

### 1. Standard Command Execution (e.g., `/report`)

This flow describes how a user command travels from Telegram to the Spoke and back.

```mermaid
sequenceDiagram
    participant U as User (Telegram)
    participant H as Hub (Cloud Run)
    participant S as Spoke (Script Spese)
    
    U->>H: /report
    Note over H: Validate User & Command
    H->>S: POST /exec (JSON Payload)
    Note right of H: { action: "generate_report", auth_key: "***" }
    
    activate S
    Note over S: 1. Validate Auth Key<br/>2. Dispatch "generate_report"<br/>3. Execute Business Logic
    S-->>H: JSON Response
    Note right of S: { success: true, message: "Report generated..." }
    deactivate S
    
    H->>U: Send Telegram Message
```

### 2. Async Automation with AI (e.g., Expense Processing)

This flow shows how the Spoke uses the Hub as a proxy to access AI services (since API keys are centralized).

```mermaid
sequenceDiagram
    participant Drive as Drive (Trigger)
    participant S as Spoke (Script Spese)
    participant H as Hub (Cloud Run)
    participant AI as Gemini / Vision API
    
    Note over Drive: User uploads file
    Drive->>S: Trigger (Time-based / Event)
    
    activate S
    S->>S: Extract Data from File
    
    %% AI Loop
    loop For each item
        S->>H: POST /api/services/gemini/analyze
        activate H
        H->>AI: Call Gemini API (using PVS Keys)
        AI-->>H: Analysis Result
        H-->>S: JSON Result
        deactivate H
    end
    
    S->>S: Update Google Sheet
    S->>H: POST /api/notify (Send Report)
    H->>U: Telegram Notification
    deactivate S
```

## 🔐 Security & Protocol

- **Authentication**: All calls from Hub to Spoke and Spoke to Hub must include the shared secret mechanism.
- **Protocol**: JSON payloads must adhere to the shared schema definitions (see `src/core/schemas.py` in Hub and `src/server/types/Protocol.ts` in Spoke).
