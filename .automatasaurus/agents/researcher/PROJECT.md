# Project Context for Researcher

Generated: 2026-02-16
Source: discovery.md, implementation-plan.md

## Recent Changes

- Initial generation from discovery and planning docs

## Overview

Stegosource is a Streamlit demo app showcasing the Anthropic Agent SDK. A Claude-powered agent dynamically rewrites `app.py` in response to user chat requests, and Streamlit hot-reloads to show changes. The demo domain is financial data visualization using Alpha Vantage. Research tasks may involve investigating SDK patterns, Streamlit behavior, API integrations, or debugging technical issues.

## Application Lifecycle

### Starting the App

```bash
uv pip install -e ".[dev]" 2>/dev/null || pip install -e ".[dev]"
streamlit run app.py --server.runOnSave=true
```

Runs at `http://localhost:8501`. Hot-reloads on file save.

### Stopping the App

```bash
pkill -f "streamlit run"
```

## Technology Stack

| Layer | Technology | Version Notes |
|-------|-----------|---------------|
| UI Framework | Streamlit | Hot-reload via `runOnSave` |
| Agent SDK | Anthropic Agent SDK (`claude-agent-sdk`) | Async-first, Python |
| Market Data | Alpha Vantage API | Free tier: 25 requests/day |
| Visualization | Plotly | Integrated via `st.plotly_chart()` |
| Configuration | python-dotenv | `.env` file for API keys |
| Package Management | pyproject.toml | Python >=3.11 |

## Key Technical Areas

### Anthropic Agent SDK
- `ClaudeSDKClient` for session management
- Built-in tools: Read, Write, Edit, Bash
- Custom tool registration for Alpha Vantage
- Streaming response handling
- System prompt design for self-modifying behavior

### Streamlit Integration
- Async/sync bridge: `asyncio.run()` to call async SDK from sync Streamlit
- Session state: `st.session_state` for conversation history
- Hot-reload: `--server.runOnSave=true` triggers rerun on file changes
- Layout: `layout="wide"`, sidebar for chat, main area for dynamic content

### Alpha Vantage API
- REST API for stock market data
- Endpoints: TIME_SERIES_DAILY, TIME_SERIES_WEEKLY, TIME_SERIES_INTRADAY
- Free tier: 25 API calls per day
- API key required (stored in `.env`)

### Self-Modifying UI Pattern
- Agent writes real Python/Streamlit/Plotly code into `app.py`
- Scaffold section (chat UI) is preserved; dynamic section is freely modified
- No predefined component schema — agent generates arbitrary Streamlit code

## Domain Terminology

| Term | Meaning |
|------|---------|
| Scaffold | The stable top section of app.py (chat, agent connection, CSS) that must not be modified by the agent |
| Dynamic section | The bottom section of app.py that the agent freely rewrites |
| Hot-reload | Streamlit automatically reruns the script when app.py is saved |
| Tool call | An SDK action (Read/Write/Edit/Bash/API call) that the agent executes |
| Candlestick chart | Financial chart showing open/high/low/close prices |

## Known Constraints

- Single-user demo (file rewriting conflicts with concurrent users)
- Alpha Vantage free tier: 25 requests/day
- Async SDK must bridge to sync Streamlit via `asyncio.run()`
- Agent can break `app.py` with bad code (error recovery is issue #11)
- No user authentication or access control

## Common Research Questions

- How does `st.session_state` behave across file-triggered reruns?
- What's the best `asyncio.run()` pattern for Streamlit + async SDKs?
- How to structure the system prompt for reliable scaffold preservation?
- Alpha Vantage API response formats and rate limit behavior
- Plotly theming for dark backgrounds in Streamlit

## Project Structure

```
stegosource/
├── app.py                 # Streamlit app (scaffold + dynamic section)
├── agent.py               # Agent SDK client, tools, system prompt
├── tools/
│   ├── __init__.py
│   └── alpha_vantage.py   # Alpha Vantage API client tool
├── .env                   # API keys (gitignored)
├── .env.example           # Template
├── .streamlit/
│   └── config.toml        # Streamlit theme
├── pyproject.toml         # Dependencies
├── logo.jpeg              # Brand logo
└── design-system.md       # Design tokens and UI patterns
```

## Reference Documents

- `discovery.md` — Full requirements, architecture, user flows
- `implementation-plan.md` — Work sequence, dependencies, risks
- `design-system.md` — Design tokens, accessibility, component patterns
