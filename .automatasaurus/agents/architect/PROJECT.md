# Project Context for Architect

Generated: 2026-02-16
Source: discovery.md, implementation-plan.md, design-system.md

## Recent Changes

- Initial generation from discovery and planning docs

## Overview

Stegosource is a Streamlit demo app where a Claude-powered agent (via Anthropic Agent SDK) dynamically rewrites its own UI file (`app.py`) in response to user chat requests. Streamlit hot-reloads to show changes. The primary architectural challenge is making this self-modifying pattern reliable: the agent must safely edit code without breaking the app, the async SDK must bridge cleanly into Streamlit's sync model, and session state must survive file-triggered reruns.

## Application Lifecycle

### Starting the App

```bash
# Install dependencies
uv pip install -e ".[dev]" 2>/dev/null || pip install -e ".[dev]"

# Start Streamlit with hot-reload
streamlit run app.py --server.runOnSave=true
```

Runs at `http://localhost:8501`. Hot-reload triggers automatically when `app.py` is saved.

### Stopping the App

```bash
# Ctrl+C in terminal, or:
pkill -f "streamlit run"
```

## High-Level Architecture

```
Streamlit App (app.py - hot-reloads on file changes)
  ├── Sidebar: Chat Interface (stable scaffold)
  │     ├── st.chat_input() - User input
  │     ├── st.chat_message() - Conversation history + tool call display
  │     └── Agent connection management
  │
  ├── Main Area: Agent-Modified Content (dynamic section)
  │     └── Whatever the agent has written: charts, forms, dashboards
  │
  └── Backend
        ├── Agent Module (agent.py)
        │     ├── ClaudeSDKClient session management
        │     ├── Tool definitions (Alpha Vantage + SDK built-ins)
        │     ├── Streaming response handler
        │     └── System prompt (scaffold preservation rules)
        │
        └── Tools
              └── alpha_vantage.py - Market data fetching
```

## Key Architectural Decisions

1. **File rewriting + hot-reload**: Agent uses SDK's Write/Edit tools on `app.py`. Streamlit's `runOnSave` handles the reload. Simple, no constraints on what agent can generate, showcases SDK capabilities.

2. **Scaffold + dynamic section**: `app.py` has a stable top section (chat UI, agent connection, CSS) and a clearly marked dynamic section the agent freely modifies. Section markers must be robust.

3. **Stateless per-rerun with history replay**: Each user message creates a fresh `query()` call with full conversation history. No persistent client across Streamlit reruns. Uses `asyncio.run()` to bridge.

4. **Single agent**: One agent with Read/Write/Edit/Bash + custom Alpha Vantage tool. No multi-agent overhead.

5. **Single-user demo**: File rewriting means concurrent users would conflict. Acceptable trade-off.

## Non-Functional Requirements

- **Reliability**: Agent-generated code must not crash the app. System prompt must strongly instruct scaffold preservation. Error recovery mechanism (issue #11) as safety net.
- **Performance**: Streamlit hot-reload is near-instant. Agent SDK streaming should display tokens as they arrive with no artificial delay.
- **Security**: API keys in `.env` (gitignored). Agent has broad tool access by design. No user auth (single-user demo). System prompt is the only guardrail for scaffold preservation.
- **Accessibility**: WCAG 2.1 AA compliance. All color combinations verified (see design-system.md). Keyboard-navigable. Screen reader considerations for charts.

## Technical Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Async SDK + sync Streamlit bridge | High | Establish `asyncio.run()` pattern cleanly in issue #2; test thoroughly |
| Session state loss on hot-reload | Medium | `st.session_state` persists by design, but verify with file changes |
| Agent breaks scaffold section | High | Robust section markers, strong system prompt, error recovery (#11) |
| Alpha Vantage rate limits (25/day) | Medium | Cache data, use mock data in dev, clear error messaging |
| Agent code generation errors | High | Error recovery mechanism (#11), syntax validation before write |

## Dependency Graph

```
#1 (Project Setup)
├── #2 (Agent SDK Client)
│   ├── #3 (Chat Interface)
│   │   └── #4 (Tool Call Display)
│   └── #5 (App Structure / Empty State)
│       ├── #7 (Plotly Charts) ── M2
│       │   └── #9 (Forms & Controls) ── M3
│       │       └── #10 (Complex Layouts) ── M3
│       ├── #11 (Error Recovery / Reset) ── M3
│       └── #12 (Visual Polish) ── M1
└── #6 (Alpha Vantage API) ── M2
    └── #8 (Error Handling) ── M2
```

## Review Criteria

When reviewing PRs, focus on:

1. **Scaffold integrity**: Does the change respect the scaffold/dynamic section boundary?
2. **Async bridge correctness**: Is `asyncio.run()` used properly? No event loop conflicts?
3. **Session state management**: Are keys consistent? Will state survive hot-reloads?
4. **System prompt quality**: Does it give the agent clear, unambiguous instructions about what to preserve?
5. **Error handling**: Graceful degradation for API failures, bad agent output, file edit errors
6. **Design system compliance**: Colors, typography, component patterns match `design-system.md`
7. **Single responsibility**: Keep `agent.py` focused on agent logic, `tools/` for tool implementations, `app.py` for UI

## Stack

| Layer | Technology |
|-------|-----------|
| UI | Python + Streamlit |
| Agent | Anthropic Agent SDK (`claude-agent-sdk`) |
| Data | Alpha Vantage API (free tier) |
| Charts | Plotly |
| Config | python-dotenv |

## Reference Documents

- `discovery.md` — Full requirements, user flows, architecture
- `implementation-plan.md` — Work sequence, dependencies, risks
- `design-system.md` — Design tokens, accessibility standards, Plotly template
