# Agent Report: implement
Completed: 2026-02-16

## Summary
Implemented Plotly chart generation support for the Stegosource agent by enhancing the system prompt with concrete chart code patterns and creating a reusable chart theming module.

## What Was Done

### 1. Created `chart_theme.py` — Reusable Chart Theming Module
- `CHART_COLORS` — 8-color sequential palette matching the design system
- `CANDLESTICK_UP` / `CANDLESTICK_DOWN` — Direction colors for candlestick charts
- `STEGO_LAYOUT` — Complete Plotly layout configuration matching the dark theme (transparent backgrounds, brand fonts, grid colors, hover styling, colorway)

### 2. Enhanced System Prompt in `agent.py`
Added a comprehensive "Chart Generation Patterns" section with:
- **Theme template guidance** — Import from `chart_theme` module, apply layout correctly (theme first, then chart-specific properties to avoid Plotly keyword conflicts)
- **Line chart example** — Complete `px.line()` pattern with data fetching, error handling, titles, axis labels, caption
- **Candlestick chart example** — Complete `go.Candlestick()` pattern with OHLC data, brand colors, range slider disabled
- **Multi-symbol comparison example** — `go.Figure()` with `add_trace()` pattern for comparing multiple stocks
- **Modifying existing charts** — Guidance on using Read + Edit tools to change charts without rewriting everything
- **Chart checklist** — 8-point verification list the agent should check before saving chart code

### 3. Added Tests
**`tests/test_agent.py`** — 14 new system prompt tests verifying:
- Chart generation section exists
- Line chart, candlestick, and multi-symbol examples present
- STEGO_LAYOUT and chart_theme import references
- Alpha Vantage import patterns
- Error handling patterns (try/except)
- Title, axis label, and caption guidance
- Candlestick color constants
- Chart modification guidance
- Chart checklist

**`tests/test_chart_theme.py`** — 15 new tests covering:
- Chart color palette (count, hex format, uniqueness, primary color)
- Candlestick direction colors (correct values, distinctness)
- STEGO_LAYOUT structure (backgrounds, fonts, title, axes, legend, hover, margins)
- Integration tests applying layout to line chart, candlestick chart, multi-trace chart
- JSON serialization verification

### Key Decisions
- Created a separate `chart_theme.py` module rather than embedding layout config inline in the system prompt. This avoids code duplication and ensures the agent can import the layout directly when writing chart code.
- Used two-step `update_layout()` pattern (theme first, then title/axes) to avoid Plotly keyword argument conflicts when both `STEGO_LAYOUT` (which has a `title` dict) and `title_text` are needed.

## Test Results
All 187 tests pass (14 new in test_agent.py + 15 new in test_chart_theme.py + 158 existing).
Lint (ruff check) and format (ruff format) both pass.

## Files Changed
- `agent.py` — Enhanced SYSTEM_PROMPT with chart generation patterns section
- `chart_theme.py` — New module with Plotly theming constants
- `tests/test_agent.py` — 14 new tests for system prompt chart content
- `tests/test_chart_theme.py` — 15 new tests for chart theming module
