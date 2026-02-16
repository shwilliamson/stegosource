# Project Context for Developer

Generated: 2026-02-16
Source: discovery.md, implementation-plan.md, design-system.md

## Recent Changes

- Initial generation from discovery and planning docs

## Overview

Stegosource is a Streamlit app that showcases the Anthropic Agent SDK by letting a Claude-powered agent dynamically rewrite its own UI (`app.py`). Users chat with the agent in a sidebar, the agent uses SDK tools (Read/Write/Edit/Bash + custom Alpha Vantage tool) to modify the app file, and Streamlit hot-reloads to show changes. This is a single-user capability demo, not a production system.

## Application Lifecycle

### Starting the App

```bash
# Install dependencies (use uv if available, otherwise pip)
uv pip install -e ".[dev]" 2>/dev/null || pip install -e ".[dev]"

# Start Streamlit with hot-reload enabled
streamlit run app.py --server.runOnSave=true
```

The app runs at `http://localhost:8501` by default.

### Stopping the App

```bash
# Ctrl+C in the terminal running streamlit
# Or find and kill the process:
pkill -f "streamlit run"
```

### Hot-Reload Behavior

- Streamlit auto-reloads when `app.py` is saved (via `--server.runOnSave=true`)
- `st.session_state` persists across reruns (chat history survives hot-reloads)
- No manual restart needed after agent edits `app.py`

### Environment Setup

```bash
# Copy env template and fill in API keys
cp .env.example .env
# Required keys: ANTHROPIC_API_KEY, ALPHAVANTAGE_API_KEY
```

## Key Technical Decisions

### Scaffold + Dynamic Section Pattern

`app.py` has two distinct regions:
1. **Scaffold section** (top): Chat interface, agent connection, CSS injection, session state management. The agent must NEVER modify this.
2. **Dynamic section** (bottom): Clearly marked area the agent freely rewrites with charts, forms, controls, dashboards.

Use clear comment markers to delineate these sections (e.g., `# === SCAFFOLD START ===` / `# === DYNAMIC SECTION START ===`).

### Async/Streamlit Bridge

The Agent SDK is async-first; Streamlit is sync. The approach:
- Each user message creates a new `query()` call with full conversation history
- Use `asyncio.run()` to bridge async SDK calls into Streamlit's sync model
- Conversation history stored in `st.session_state` and replayed each turn
- No persistent client across Streamlit reruns

### Agent Architecture

- Single agent with `ClaudeSDKClient` in `agent.py`
- Tools: SDK built-ins (Read, Write, Edit, Bash) + custom Alpha Vantage tool
- System prompt instructs agent about app structure, scaffold preservation, and how to write Streamlit/Plotly code
- Streaming responses displayed in real-time in chat

## Project Structure (Target)

```
stegosource/
├── app.py                 # Streamlit app (scaffold + dynamic section)
├── agent.py               # Agent SDK client, tool definitions, system prompt
├── tools/
│   ├── __init__.py
│   └── alpha_vantage.py   # Alpha Vantage API client tool
├── .env                   # API keys (gitignored)
├── .env.example           # Template for required env vars
├── .streamlit/
│   └── config.toml        # Streamlit theme configuration
├── pyproject.toml         # Dependencies (pinned versions)
├── logo.jpeg              # Brand logo
└── README.md
```

## Stack

| Layer | Technology |
|-------|-----------|
| UI Framework | Python + Streamlit (hot-reload via `runOnSave`) |
| Agent Orchestration | Anthropic Agent SDK (`claude-agent-sdk`) |
| Market Data | Alpha Vantage API (free tier, 25 req/day) |
| Visualization | Plotly |
| Configuration | python-dotenv + `.env` file |

## Design System Reference

All UI code must follow `design-system.md`. Key points:

- **Dark theme**: Use `.streamlit/config.toml` for primary theming
- **CSS custom properties**: Inject `CUSTOM_CSS` block once in the scaffold section
- **Plotly template**: Use the `PLOTLY_TEMPLATE` dict from design-system.md for all charts
- **Colors**: Brand cyan `#00D4FF`, magenta `#E040A0`, green `#00E676`
- **Candlestick**: Up = green (#00E676), Down = magenta (#E040A0)
- **Charts**: Always `st.plotly_chart(fig, use_container_width=True)`, transparent backgrounds
- **Forms**: `type="primary"` on submit buttons, label all inputs
- **Layout**: `layout="wide"` always, use `st.columns()` for multi-element layouts

## Implementation Notes

- **Chat interface**: Lives in sidebar with `st.chat_input()`, `st.chat_message()`, and `st.session_state` for history
- **Tool call display**: Show tool calls in `st.expander()` inside assistant messages with descriptive labels ("Editing app.py", "Fetching AAPL data")
- **Empty state**: Centered in main area with logo, tagline, and 3-4 clickable example prompt buttons
- **Error handling**: Inline chat errors for bad input, `st.toast()` for transient issues, `st.warning()` for persistent issues (missing API key)
- **Alpha Vantage**: Client in `tools/alpha_vantage.py`, handle free tier rate limits (25/day) with user-facing messages

## Common Pitfalls

- Don't forget `asyncio.run()` bridge when calling async Agent SDK from Streamlit
- Session state key names must be consistent across reruns
- The agent system prompt is critical — poorly designed prompts lead to the agent breaking the scaffold
- Alpha Vantage free tier is extremely limited; consider mock/cached data for development
- Plotly charts need transparent backgrounds to match the dark theme (`paper_bgcolor="rgba(0,0,0,0)"`)

## Reference Documents

- `discovery.md` — Full requirements and user flows
- `implementation-plan.md` — Work sequence and dependencies
- `design-system.md` — Design tokens, components, Plotly template, accessibility
