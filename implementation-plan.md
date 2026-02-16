# Implementation Plan

Generated: 2026-02-16
Based on: 12 open issues across 3 milestones

## Summary

| Milestone | Issues | Status |
|-----------|--------|--------|
| Milestone 1: Foundation & Agent Chat | 6 | 0 complete / 6 total |
| Milestone 2: Data Fetching & Visualization | 3 | 0 complete / 3 total |
| Milestone 3: Dynamic UI & Full Demo Loop | 3 | 0 complete / 3 total |

## Work Sequence

### Phase 1: Milestone 1 — Foundation & Agent Chat

#### 1. Issue #1: Set up project structure, dependencies, and environment configuration
- **Why first**: No dependencies. Foundation for everything else.
- **Unblocks**: #2, #6
- **Estimated complexity**: Low
- **Key work**: Project scaffolding, pinned dependencies in pyproject.toml, .env/.env.example setup, directory structure (agent.py, tools/), Streamlit config for hot-reload

#### 2. Issue #2: Implement Agent SDK client with streaming and system prompt
- **Why now**: Depends on #1 (project structure). Core integration piece.
- **Unblocks**: #3, #5
- **Estimated complexity**: High
- **Key work**: ClaudeSDKClient wrapper in agent.py, streaming response handler, system prompt design (instruct agent about app structure, scaffold preservation), tool registration, asyncio bridge for Streamlit

#### 3. Issue #5: Structure app.py with scaffold/dynamic sections and empty state
- **Why now**: Depends on #2. Unblocks the most downstream issues (3 issues).
- **Unblocks**: #7, #11, #12
- **Estimated complexity**: Medium
- **Key work**: Define scaffold section (chat UI, agent connection) vs dynamic section (agent-modifiable area) in app.py, clear section markers/comments, empty state with clickable example prompts, layout="wide" setup

#### 4. Issue #3: Build Streamlit chat interface with streaming display
- **Why now**: Depends on #2. Core user-facing feature.
- **Unblocks**: #4
- **Estimated complexity**: Medium
- **Key work**: Sidebar chat with st.chat_input(), message history via st.chat_message(), streaming display of agent responses, conversation state in st.session_state, loading indicators

#### 5. Issue #4: Display agent tool calls in the chat UI
- **Why now**: Depends on #3 (chat interface must exist first).
- **Unblocks**: None directly (but critical for demo value)
- **Estimated complexity**: Medium
- **Key work**: Intercept tool call events from streaming, render in expandable st.expander() sections within chat messages, show tool name, inputs, and outputs, contextual labels ("Editing app.py...", "Fetching data...")

#### 6. Issue #12: Visual polish and branding with logo
- **Why now**: Depends on #5 (app structure). Lower priority — polish after core features.
- **Unblocks**: None
- **Estimated complexity**: Low
- **Key work**: Logo/branding in sidebar header, consistent color theme (per design system), typography refinement, overall visual polish pass

### Phase 2: Milestone 2 — Data Fetching & Visualization

#### 7. Issue #6: Implement Alpha Vantage API client as a custom agent tool
- **Why now**: Depends on #1 (already complete by this phase). First M2 issue, enables data fetching.
- **Unblocks**: #8
- **Estimated complexity**: Medium
- **Key work**: Alpha Vantage client in tools/alpha_vantage.py, support for daily/weekly/intraday time series, register as custom agent tool, handle API key from .env, return structured data suitable for charting

#### 8. Issue #7: Agent generates Plotly charts via file editing and hot-reload
- **Why now**: Depends on #5 (app structure with dynamic section). Core visualization feature.
- **Unblocks**: #9
- **Estimated complexity**: High
- **Key work**: Agent writes Plotly code into app.py's dynamic section, support for line/candlestick/bar charts, st.plotly_chart() with use_container_width=True, agent can modify existing charts (change type, add data), hot-reload verification

#### 9. Issue #8: Implement error handling for API limits, bad input, and agent failures
- **Why now**: Depends on #6 (Alpha Vantage client). Polish for data layer.
- **Unblocks**: None
- **Estimated complexity**: Medium
- **Key work**: Inline chat errors for bad requests, toast notifications for rate limits (25/day free tier), persistent warnings for missing API keys, graceful handling of agent errors and failed file edits

### Phase 3: Milestone 3 — Dynamic UI & Full Demo Loop

#### 10. Issue #9: Agent generates functional Streamlit forms and controls
- **Why now**: Depends on #7 (chart generation). Builds interactive controls on top of visualizations.
- **Unblocks**: #10
- **Estimated complexity**: High
- **Key work**: Agent writes date pickers, dropdowns, selectors into app.py, form submission triggers data re-fetch and chart update, controls interact with existing chart data, functional wiring (not just UI)

#### 11. Issue #10: Agent creates complex layouts: dashboards, columns, and tabs
- **Why now**: Depends on #9 (forms/controls). Most advanced UI generation.
- **Unblocks**: None
- **Estimated complexity**: High
- **Key work**: Agent writes multi-chart dashboards, st.columns() layouts, st.tabs() navigation, complex compositions combining charts + controls + text, responsive layout considerations

#### 12. Issue #11: Error recovery and workspace reset mechanism
- **Why now**: Depends on #5 (app structure). Can be worked after #10 or in parallel with M3 features.
- **Unblocks**: None
- **Estimated complexity**: Medium
- **Key work**: "Reset workspace" button to restore app.py to default state, save/restore original app.py content, handle broken code recovery (agent edits that crash the app), session cleanup

## Dependency Graph

```
#1 (Project Setup)
├── #2 (Agent SDK Client)
│   ├── #3 (Chat Interface)
│   │   └── #4 (Tool Call Display)
│   └── #5 (App Structure / Empty State)
│       ├── #7 (Plotly Charts) ─── M2
│       │   └── #9 (Forms & Controls) ─── M3
│       │       └── #10 (Complex Layouts) ─── M3
│       ├── #11 (Error Recovery / Reset) ─── M3
│       └── #12 (Visual Polish) ─── M1
└── #6 (Alpha Vantage API) ─── M2
    └── #8 (Error Handling) ─── M2
```

### Parallelization Opportunities

Within the sequential workflow, some issues share the same dependency and could theoretically be worked in parallel:

| After completing | Can start in parallel |
|------------------|-----------------------|
| #2 | #3 and #5 (both depend only on #2) |
| #5 | #7, #11, and #12 (all depend only on #5) |
| #1 | #2 and #6 (both depend only on #1, but #6 is M2) |

## Design Foundation

**Design System:** `design-system.md`

All UI implementations must follow the design system for a cohesive user experience. The design system covers:
- Color palette (tech-forward, data-focused)
- Typography (Streamlit-compatible)
- Component patterns (chat messages, tool calls, charts, forms)
- Accessibility standards

## Blockers & Risks

- **Agent SDK async + Streamlit sync**: The asyncio bridge (asyncio.run()) is a known friction point. Issue #2 must establish this pattern cleanly for everything else to work.
- **Hot-reload state preservation**: Streamlit reruns on file change may reset some session state. Issue #5 needs to verify that st.session_state (chat history) survives hot-reloads.
- **Scaffold preservation**: The agent must reliably preserve the scaffold section when editing app.py. System prompt design in #2 is critical, and #5's section markers must be robust.
- **Alpha Vantage rate limits**: Free tier allows 25 requests/day. Development and testing will consume quota quickly. Consider caching or mock data for development.
- **Agent code generation reliability**: The agent writes real Python code — syntax errors will crash the app. Issue #11 (error recovery) is important but comes late in the sequence.

## Notes

- Issues #3 and #5 can be worked in parallel after #2, which could accelerate Milestone 1 completion
- Issue #6 technically only depends on #1, so it could start early — but completing Milestone 1 first gives the agent client and app structure needed for integration testing
- Issue #12 (visual polish) is deliberately last in Milestone 1 to avoid rework as the UI stabilizes
- The system prompt (part of #2) is arguably the most important artifact — it determines how well the agent modifies the app without breaking things
