# Project Context for Designer

Generated: 2026-02-16
Source: discovery.md, implementation-plan.md, design-system.md

## Recent Changes

- Initial generation from discovery and planning docs

## Overview

Stegosource is a dark-themed Streamlit demo app where users chat with a Claude-powered AI agent that dynamically rewrites the app's UI. The design challenge is creating a cohesive visual experience where agent-generated content (charts, forms, dashboards) blends seamlessly with the stable scaffold (chat interface). The brand identity is rooted in a circuit-board stegosaurus logo with neon cyan accents on a dark background.

## Application Lifecycle

### Viewing the App

```bash
# Start the app
streamlit run app.py --server.runOnSave=true
```

Opens at `http://localhost:8501`. The app hot-reloads when files change — no manual refresh needed.

## Users

| User Type | Needs |
|-----------|-------|
| Demo viewer | See Agent SDK capabilities in action, interact via chat, see tool use transparency |
| Developer | Explore SDK patterns, understand capabilities and limits |

## Design Philosophy

1. **Dark-first, data-forward** — Dark backgrounds make charts pop and signal a technical tool
2. **Restrained color** — Mostly neutral darks. Color reserved for brand accents, data, semantic states
3. **Visible intelligence** — Tool calls, streaming text, state changes feel transparent
4. **Streamlit-native** — Work with the framework. Use `config.toml` theming primarily, CSS injection sparingly

## Key User Flows

### Flow 1: First-Time Experience
1. App loads with empty state: centered logo, tagline, 3-4 clickable example prompts
2. User clicks an example prompt → auto-sends to chat
3. Agent processes, edits app.py, UI hot-reloads with chart

### Flow 2: Data Request
1. User types request in sidebar chat
2. Agent tool calls appear in expandable sections (visible intelligence)
3. App hot-reloads with new visualization

### Flow 3: UI Modification
1. User requests UI changes ("add date picker", "switch to candlestick")
2. Agent edits app.py, hot-reload shows new controls/chart type

## Layout Structure

```
+--------------------------------------------+
|  SIDEBAR (~350px)  |    MAIN AREA (fluid)   |
|                    |                         |
|  [Logo]            |  [Agent-generated UI]   |
|  [Chat history]    |  - Charts               |
|  [Tool calls]      |  - Forms                |
|  [Chat input]      |  - Dashboards           |
|                    |  - Empty state           |
+--------------------------------------------+
```

- Always `layout="wide"`
- Sidebar: fixed ~350px (Streamlit default)
- Main area: fluid, fills remaining space

## Design System

The full design system is in `design-system.md`. Key references:

### Brand Colors
- `brand-cyan`: #00D4FF (primary accent)
- `brand-magenta`: #E040A0 (secondary accent, candlestick down)
- `brand-green`: #00E676 (success, candlestick up)

### Dark Theme
- `bg-primary`: #0E1117 (app background)
- `bg-secondary`: #1A1D26 (sidebar, cards)
- `bg-elevated`: #262A36 (tooltips, dropdowns)

### Text
- `text-primary`: #FAFAFA
- `text-secondary`: #A0A8B8
- `text-tertiary`: #787E8C

### Key Component Patterns

| Component | Implementation |
|-----------|---------------|
| Chat messages | `st.chat_message()` in sidebar, native styling |
| Tool calls | `st.expander()` inside assistant messages with material icons |
| Empty state | Centered logo + tagline + 2x2 button grid |
| Charts | `st.plotly_chart(fig, use_container_width=True)` with PLOTLY_TEMPLATE |
| Forms | Standard Streamlit widgets, `type="primary"` on submit |
| Status | `st.success/warning/error/info` for semantic feedback |

### Logo
- File: `logo.jpeg`
- Sidebar: `st.sidebar.image("logo.jpeg", width=200)`
- Empty state: centered, `width=280`
- Alt text: "Stegosource — Dynamic Data Agent"

## Accessibility Requirements (WCAG 2.1 AA)

- All color combinations verified for contrast (see design-system.md)
- Keyboard navigation via Streamlit defaults
- Descriptive labels on all buttons and form widgets
- `st.caption()` below charts describing the data shown
- Heading hierarchy: `st.header()` / `st.subheader()`, no skipped levels
- Charts include axis labels, chart titles, and informative hover templates
- Candlestick direction (up/down) conveyed in hover text, not just color
- Minimum 44x44px touch targets (Streamlit widgets meet this)

## Brand Voice

- Technical but approachable
- Concise — short sentences, no filler
- Confident — "Here's your chart" not "I hope this helps!"
- No emoji in agent text

## Reference Documents

- `design-system.md` — Complete design tokens, Plotly template, component patterns, accessibility audit
- `discovery.md` — Full requirements and user flows
- `implementation-plan.md` — Work sequence and dependencies
