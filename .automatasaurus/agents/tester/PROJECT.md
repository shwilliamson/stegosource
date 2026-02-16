# Project Context for Tester

Generated: 2026-02-16
Source: discovery.md, implementation-plan.md, design-system.md

## Recent Changes

- Initial generation from discovery and planning docs

## Overview

Stegosource is a Streamlit demo app where a Claude-powered agent dynamically rewrites `app.py` to generate charts, forms, and dashboards from user chat requests. Testing focuses on verifying the chat interface, tool call visibility, hot-reload behavior, data visualization, and the self-modifying UI pattern. This is a single-user demo — no multi-user or auth testing needed.

## Application Lifecycle

### Starting the App for Testing

```bash
# Install dependencies
uv pip install -e ".[dev]" 2>/dev/null || pip install -e ".[dev]"

# Start Streamlit with hot-reload
streamlit run app.py --server.runOnSave=true
```

The app runs at **http://localhost:8501**.

### Stopping the App

```bash
# Ctrl+C in the terminal, or:
pkill -f "streamlit run"
```

### Reloading

The app auto-reloads when `app.py` is saved (via `--server.runOnSave=true`). No manual restart needed unless you change dependencies or `.streamlit/config.toml`.

### Testing with Playwright MCP

You have access to the Playwright MCP server for browser-based E2E testing. Use it to:

1. **Navigate** to the app: `browser_navigate` to `http://localhost:8501`
2. **Take snapshots**: `browser_snapshot` to inspect the accessibility tree (preferred over screenshots for interaction)
3. **Take screenshots**: `browser_take_screenshot` for visual verification
4. **Interact**: `browser_click`, `browser_type`, `browser_fill_form` to test user flows
5. **Wait for elements**: `browser_wait_for` to handle async loading and hot-reloads
6. **Check console**: `browser_console_messages` for JavaScript errors

#### Headless Mode (GitHub Codespace)

This project runs in a GitHub Codespace — there is **no display server**. The Playwright MCP browser runs in **headless mode** automatically. This means:

- **No visual browser window** — you cannot see the browser, only interact programmatically
- **`browser_snapshot` is your primary tool** — the accessibility tree is the most reliable way to understand page state. Use it before every interaction.
- **`browser_take_screenshot`** still works and produces image files — use it for visual verification of layout, colors, and chart rendering. You can read the screenshot file to inspect it.
- **All interactions work normally** — clicking, typing, form fills, navigation all function identically in headless mode.
- **No `--ui` mode available** — Playwright's interactive UI runner won't work. All testing is done via MCP tool calls.

#### Typical Playwright MCP Test Flow

```
1. Start the app (if not running): streamlit run app.py --server.runOnSave=true &
2. Navigate: browser_navigate to http://localhost:8501
3. Wait for load: browser_wait_for text "Stegosource" (or relevant UI text)
4. Snapshot: browser_snapshot to get the accessibility tree
5. Interact: click buttons, type in inputs, verify elements
6. Screenshot: browser_take_screenshot for visual evidence
7. Verify: check that expected elements/text/charts are present
```

#### Important Playwright MCP Notes

- Always use `browser_snapshot` before interacting — it gives you the element refs needed for clicks/typing
- After Streamlit hot-reload, wait briefly then re-snapshot to get updated element refs
- Streamlit widgets have specific accessibility roles — use the snapshot to find them
- The sidebar chat input is a standard `st.chat_input()` — look for a textbox role
- Charts render as Plotly iframes — you may need to check for the container rather than chart internals
- In headless mode, default viewport is typically 1280x720 — use `browser_resize` if you need to test responsive behavior at different sizes

## Critical User Journeys

### Journey 1: First-Time Experience (Empty State)
1. Open app → main area shows logo, tagline, 3-4 example prompt buttons
2. Sidebar has chat input, no messages yet
3. Example prompts are clickable and keyboard-accessible
4. Clicking a prompt sends it as a chat message

### Journey 2: Basic Data Request
1. User types "Show me AAPL stock for the last 3 months" in sidebar chat
2. Agent processes: tool calls appear in expandable sections
3. App hot-reloads with a Plotly chart in the main area
4. Agent confirms in chat

### Journey 3: Chart Type Morphing
1. User has a line chart displayed
2. User types "Switch to candlestick chart"
3. Agent edits app.py, hot-reload shows candlestick chart
4. Chart uses correct colors (green up, magenta down)

### Journey 4: Dynamic UI Generation
1. User requests "Add a date range picker"
2. Agent adds form controls to app.py
3. Hot-reload shows new widgets
4. Widgets are functional (not just visual)

### Journey 5: Error Recovery
1. Agent writes broken code → Streamlit shows error
2. User can still use chat to ask agent to fix it
3. "Reset workspace" restores app.py to default (issue #11)

## Acceptance Criteria by Issue

### Milestone 1: Foundation & Agent Chat

**#1 - Project Setup**: Dependencies install cleanly, `.env.example` exists, `streamlit run` starts without errors

**#2 - Agent SDK Client**: Agent responds to messages, streaming works, tool calls execute, `asyncio.run()` bridge functions correctly

**#3 - Chat Interface**: Chat input in sidebar, messages display with `st.chat_message()`, streaming responses render progressively, conversation state persists across reruns

**#4 - Tool Call Display**: Tool calls shown in expandable sections, descriptive labels, content visible when expanded, icons match tool type

**#5 - App Structure**: Clear scaffold/dynamic sections, empty state with logo + example prompts, example prompts trigger chat messages, `layout="wide"` active

**#12 - Visual Polish**: Logo in sidebar, design system colors applied, consistent typography

### Milestone 2: Data Fetching & Visualization

**#6 - Alpha Vantage Tool**: Fetches stock data correctly, handles API key from `.env`, returns structured data

**#7 - Plotly Charts**: Charts render in dynamic section, correct colors per design system, `use_container_width=True`, supports line/candlestick/bar

**#8 - Error Handling**: Invalid tickers show inline errors, rate limits show toast/warning, missing API key shows persistent warning

### Milestone 3: Dynamic UI & Full Demo Loop

**#9 - Forms & Controls**: Agent generates functional widgets, form submission triggers data update, controls interact with charts

**#10 - Complex Layouts**: Multi-chart dashboards, `st.columns()` layouts, `st.tabs()` navigation

**#11 - Error Recovery**: Reset button restores app.py to default, broken code recovery possible via chat

## Edge Cases to Test

- Empty ticker input
- Invalid ticker symbol (e.g., "XYZNOTREAL")
- API rate limit hit (25/day on free tier)
- Missing `.env` or missing API keys
- Agent edits that break `app.py` syntax
- Very long chat conversations (session state growth)
- Multiple rapid requests while agent is processing
- Hot-reload during streaming response

## Design System Verification

When verifying UI, check against `design-system.md`:
- Dark theme active (bg-primary: #0E1117)
- Brand cyan (#00D4FF) used for primary accent/links
- Text is readable (WCAG AA contrast ratios)
- Charts use the defined color palette
- Forms use `type="primary"` on submit buttons
- Logo displays correctly in sidebar and empty state

## Reference Documents

- `discovery.md` — Full requirements and user flows
- `implementation-plan.md` — Work sequence and dependencies
- `design-system.md` — Visual specs, accessibility requirements, component patterns
