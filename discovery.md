# Discovery: Stegosource - Dynamic Data Visualization Agent

## Overview
Stegosource is a demo app that showcases the Anthropic Agent SDK's capabilities when exposed directly to end users. Users interact with a Claude-powered agent through a chat interface embedded in a Streamlit app. The agent has full access to Agent SDK tools -- including file editing, bash commands, and code execution -- and uses them to **dynamically rewrite the Streamlit app itself**, which hot-reloads to show the changes.

The primary goal is to explore and demonstrate what happens when you give an AI agent the power to modify its own UI in response to natural language requests. This is a capability demo, not a production architecture.

## Goals
- Demonstrate the Anthropic Agent SDK's full capabilities (tool use, file editing, code execution, streaming, multi-turn conversation) in a user-facing application
- Showcase the self-modifying UI pattern: agent rewrites `app.py`, Streamlit hot-reloads the changes
- Provide conversational financial data exploration as a compelling demo domain
- Make agent tool use visible in the UI so viewers understand what the SDK is doing
- Serve as a learning/exploration vehicle for Agent SDK patterns

## Users
| User Type | Needs | Permissions |
|-----------|-------|-------------|
| Demo viewer | See the Agent SDK capabilities in action, interact with the agent via chat | Full chat access, can request any UI change or data |
| Developer (self) | Explore Agent SDK patterns, understand capabilities and limits | Full access, can modify and extend |

## Requirements

### Must Have (MVP)

#### Agent SDK Integration
- Agent powered by `claude-agent-sdk` Python package
- Agent has access to SDK built-in tools: Read, Write, Edit, Bash
- Custom tool for Alpha Vantage data fetching
- Multi-turn conversational session using `ClaudeSDKClient`
- Streaming responses displayed in real-time in the chat
- Agent can execute arbitrary code and bash commands as part of the demo
- `.env` file for API keys (`ANTHROPIC_API_KEY`, `ALPHAVANTAGE_API_KEY`)

#### Self-Modifying UI (File Rewriting + Hot Reload)
- Agent modifies `app.py` (or designated UI files) using SDK's Write/Edit tools
- Streamlit runs with `--server.runOnSave=true` to hot-reload on file changes
- Agent can add/modify/remove any Streamlit component: forms, charts, controls, layouts
- No predefined component schema -- the agent writes real Streamlit/Plotly code directly
- The app file has a stable "scaffold" section (chat interface, agent connection) that the agent preserves, and a "dynamic" section that the agent freely modifies

#### Streamlit Chat Interface
- Chat input in the Streamlit sidebar
- Chat history displayed with `st.chat_message()` components
- Conversation state persisted in `st.session_state`
- Streaming agent responses rendered progressively
- Visual feedback during agent processing

#### Visible Tool Use
- The chat UI displays agent tool calls as they happen (e.g., "Editing app.py...", "Running bash command...", "Fetching AAPL data...")
- Tool calls shown in expandable sections so the user can see what the agent did
- This is what differentiates the demo from a generic chat app -- viewers see the SDK at work

#### Data Fetching
- Alpha Vantage API client as a custom agent tool
- Fetch stock time series data (daily, weekly, intraday)
- Handle free tier limitations (25 requests/day) with clear error messaging

#### Visualization
- Agent writes Plotly chart code directly into the app
- Support for line charts, candlestick charts, bar charts
- Charts rendered via `st.plotly_chart()` with `use_container_width=True`
- Responsive layout using Streamlit's `layout="wide"` mode

#### Empty State & Onboarding
- When the app first loads, show a brief description and 3-4 clickable example prompts
- Examples like: "Show me AAPL stock for the last 3 months", "Add a date range picker", "Compare TSLA and F"
- Clicking an example populates the chat and sends the message
- Empty state disappears once the agent has generated content

#### Error Handling
- Inline chat errors for bad requests (invalid ticker, etc.)
- Toast notifications for transient issues (rate limits)
- Persistent warnings for session-wide issues (missing API key)
- Graceful handling of agent errors or failed file edits

### Nice to Have
- Multi-symbol comparison dashboards
- Volume subplots beneath price charts
- Technical indicators (moving averages)
- Agent reasoning visibility (thinking process, not just tool calls)
- "Reset workspace" button to restore app.py to its default state
- Session info display (model, tokens consumed)

## User Flows

### Flow 1: Basic Data Request
1. User types "Show me AAPL stock for the last 3 months" in sidebar chat
2. Agent calls Alpha Vantage tool to fetch data (tool call visible in chat)
3. Agent uses Edit tool to add a Plotly chart to app.py (tool call visible)
4. Streamlit hot-reloads, chart appears in main area
5. Agent confirms in chat: "Here's Apple's daily stock price for the last 3 months"

### Flow 2: Dynamic UI Generation
1. User types "Let me adjust the date range"
2. Agent uses Edit tool to add date picker widgets to app.py (visible in chat)
3. Streamlit hot-reloads, date pickers appear in the main area
4. User adjusts dates and clicks apply
5. The form triggers a data re-fetch and chart update

### Flow 3: Chart Type Morphing
1. User has a line chart displayed
2. User types "Switch to candlestick chart"
3. Agent reads current app.py, edits the chart code to use candlestick
4. Streamlit hot-reloads with the new chart type

### Flow 4: Arbitrary Code Execution
1. User types "Create a dashboard comparing the top 5 tech stocks"
2. Agent writes bash commands to fetch data, generates complex layout code
3. Agent edits app.py with a multi-chart dashboard layout
4. Streamlit hot-reloads with the full dashboard

### Flow 5: First-Time Experience
1. User opens the app for the first time
2. Main area shows description + example prompts
3. User clicks "Show me AAPL stock for the last 3 months"
4. Message auto-sends, Flow 1 begins

## Architecture

### System Design
```
Streamlit App (app.py - hot-reloads on file changes)
  ├── Sidebar: Chat Interface (stable scaffold)
  │     ├── st.chat_input() - User input
  │     ├── st.chat_message() - Conversation history with tool call display
  │     └── Agent connection management
  │
  ├── Main Area: Agent-Modified Content (dynamic section)
  │     ├── Whatever the agent has written: charts, forms, controls, dashboards
  │     └── Empty state with example prompts (before first agent modification)
  │
  └── Backend
        ├── Agent Module (agent.py)
        │     ├── ClaudeSDKClient session management
        │     ├── Tool definitions (Alpha Vantage + SDK built-ins)
        │     ├── Streaming response handler
        │     └── System prompt instructing agent how to modify the app
        │
        └── Tools
              └── alpha_vantage.py - Market data fetching (custom tool)
```

### Key Technical Decisions
- **File rewriting + hot reload**: The agent uses SDK's built-in Write/Edit tools to modify `app.py` directly. Streamlit's `runOnSave` hot-reloads the UI. This is simpler, imposes no constraints on what the agent can generate, and showcases the SDK's core file-editing capabilities.
- **Agent SDK with full tool access**: The agent gets Read, Write, Edit, Bash plus a custom Alpha Vantage tool. This demonstrates the SDK's power -- the agent can do anything a developer can do.
- **Scaffold + dynamic section pattern**: `app.py` has a stable top section (chat interface, agent connection) that the agent is instructed to preserve, and a clearly marked dynamic section that the agent freely modifies.
- **Single agent architecture**: One agent with well-designed tools and a good system prompt. No multi-agent overhead needed for this demo scope.
- **Visible tool use**: Every tool call the agent makes is displayed in the chat UI, making the SDK's behavior transparent to demo viewers.
- **Single-user demo**: This is explicitly a single-user demo app. File rewriting means concurrent users would conflict. This is an acceptable trade-off for a capability showcase.

### Stack
| Layer | Technology |
|-------|-----------|
| UI Framework | Python + Streamlit (hot-reload) |
| Agent Orchestration | Anthropic Agent SDK (`claude-agent-sdk`) |
| Market Data | Alpha Vantage API (free tier) |
| Visualization | Plotly |
| Configuration | python-dotenv + `.env` file |

### Project Structure (Target)
```
stegosource/
├── app.py                 # Streamlit app (scaffold + dynamic section)
├── agent.py               # Agent SDK client, tool definitions, system prompt
├── tools/
│   ├── __init__.py
│   └── alpha_vantage.py   # Alpha Vantage API client tool
├── .env                   # API keys (gitignored)
├── .env.example           # Template for required env vars
├── pyproject.toml         # Dependencies (pinned versions)
└── README.md
```

### Async/Streamlit Integration Strategy
The Agent SDK is async-first; Streamlit is synchronous. The chosen approach:
- **Stateless per-rerun with history replay**: Each user message creates a new `query()` call with the full conversation history passed as context. No persistent client across Streamlit reruns.
- Use `asyncio.run()` to bridge async SDK calls into Streamlit's sync execution model.
- Conversation history stored in `st.session_state` and replayed each turn.
- This is the simplest approach and appropriate for a demo.

## UI/UX Requirements
- Sidebar contains the chat interface (input + history + tool call display)
- Main area is fully controlled by the agent's code modifications
- Tool calls shown in expandable/collapsible sections within chat messages
- Empty state with clickable example prompts before first agent interaction
- Loading indicators during agent processing with contextual messages ("Thinking...", "Editing app.py...", "Fetching data...")
- Hot-reload may cause brief flash -- acceptable for a demo, but minimize disruption where possible

## Security
- API keys stored in `.env`, never committed (`.gitignore`)
- `.env.example` provided as a template
- Agent has broad tool access by design (this is the demo's purpose)
- No user authentication (single-user demo)
- System prompt instructs agent to preserve the scaffold section of app.py
- Alpha Vantage API key scoped to free tier

## Out of Scope
- SQLite/MCP persistence layer (future milestone)
- Price alerts and notifications
- User authentication / multi-user support
- Runtime rendering / component spec approach
- Production deployment / containerization
- Mobile-specific responsive design
- Agent sandboxing beyond system prompt guardrails

## Open Questions
- How to best structure the "scaffold" vs "dynamic" sections of app.py to minimize the chance the agent breaks the chat interface when editing?
- What's the best way to preserve `st.session_state` (chat history) across hot-reloads? (Streamlit generally preserves session state across reruns, but file changes may reset some state.)
- Should there be a "reset to default" mechanism that restores app.py to its original state?

## Proposed Milestones

### Milestone 1: Foundation & Agent Chat
- Set up project structure, dependencies (pinned versions), and `.env` configuration
- Implement Agent SDK integration with `ClaudeSDKClient` and streaming
- Build the Streamlit chat interface in the sidebar (input, message history, streaming display)
- Display agent tool calls in the chat UI (expandable sections)
- Create a basic agent with a system prompt that understands the app structure
- Agent can hold a conversation and use Read/Write/Edit on app.py
- Empty state with example prompts in the main area

### Milestone 2: Data Fetching & Visualization
- Implement Alpha Vantage API client as a custom agent tool
- Agent can fetch stock data and write Plotly chart code into app.py
- Charts render after hot-reload
- Handle API errors and free tier rate limiting with user-facing messages
- Agent can modify existing charts (change type, add data, adjust layout)

### Milestone 3: Dynamic UI & Full Demo Loop
- Agent can generate functional Streamlit forms and controls (date pickers, dropdowns, selectors)
- Controls interact with chart data (form submission triggers data update)
- Agent can create complex layouts (multi-chart dashboards, columns, tabs)
- Wire up the full demo loop: chat request → agent edits app.py → hot-reload → user interacts with new UI → agent responds
- Error handling for all edge cases (bad edits, broken code, recovery)
- "Reset workspace" capability to restore app.py to default
