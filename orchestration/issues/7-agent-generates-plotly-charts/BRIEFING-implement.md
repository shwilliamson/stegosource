# Agent Briefing: implement
Generated: 2026-02-16

## Your Task
Implement issue #7: Agent generates Plotly charts via file editing and hot-reload

## Context
- This issue is about enhancing the agent's system prompt and providing concrete chart generation patterns so the Claude agent can reliably produce working Plotly chart code in the dynamic section of `app.py`.
- The Alpha Vantage tool (#6) and app scaffold (#5) are already implemented.
- Mode: all-issues

## Acceptance Criteria (from issue)
- [ ] Agent can write Plotly chart code into the dynamic section of `app.py`
- [ ] Line charts render correctly with time series data (date on x-axis, price on y-axis)
- [ ] Candlestick charts render correctly with OHLC data
- [ ] Charts use `st.plotly_chart(fig, use_container_width=True)` for responsive sizing
- [ ] Charts have proper titles, axis labels, and legends
- [ ] Streamlit hot-reloads after the agent edits app.py, showing the new chart
- [ ] Agent can modify an existing chart (e.g., change from line to candlestick, add a new symbol)
- [ ] Agent writes the data-fetching logic into app.py (using the Alpha Vantage tool to get data, then embedding it or fetching it inline)

## Current State Analysis
The system prompt in `agent.py` already has general guidance about chart generation, but it lacks:
1. **Concrete code examples** showing exactly how to write a line chart or candlestick chart
2. **Data-fetching pattern** showing how to call `fetch_daily`/`fetch_intraday` inline in app.py
3. **Error handling pattern** for when data fetching fails in the dynamic section
4. **Chart styling guidance** for titles, axis labels, legends, and theming
5. **Modification patterns** showing how to replace/extend existing chart code

## What to Implement

### 1. Enhance the System Prompt in `agent.py`
Add concrete chart code examples to the SYSTEM_PROMPT that show:
- How to import and use `fetch_daily`/`fetch_intraday` in the dynamic section
- A working line chart pattern with Plotly Express
- A working candlestick chart pattern with Plotly Graph Objects
- Proper chart titles, axis labels, and legends
- Error handling for data fetching in the dynamic section
- How to modify/replace existing charts

### 2. Add Tests for Chart Generation Patterns
Create tests that verify:
- The system prompt contains chart-related instructions
- Chart code patterns mentioned in the system prompt are syntactically valid
- The agent module properly exports/references the needed plotly patterns

### 3. Key Files to Modify
- `agent.py` - Enhance SYSTEM_PROMPT with concrete chart examples and patterns
- `tests/test_agent.py` - Add tests for chart-related system prompt content

### 4. Key Files to Read (as needed)
- `app.py` - Understand the dynamic section structure
- `tools/alpha_vantage.py` - Understand the fetch functions API
- `design-system.md` - Check for any chart theming/color tokens
- `tests/test_app.py` - Existing test patterns
- `tests/test_alpha_vantage.py` - Existing test patterns

## Technical Notes
- The agent edits `app.py` directly using the SDK's Write/Edit tools
- Plotly Express (`px.line`, `px.scatter`) for simple charts; Plotly Graph Objects (`go.Candlestick`) for complex ones
- The agent needs to write self-contained code in the dynamic section -- the chart code must work when Streamlit re-runs the file
- Data can be fetched inline in app.py using `from tools.alpha_vantage import fetch_daily, fetch_intraday`
- Hot-reload: Streamlit re-runs the entire file on save, so the chart code executes fresh each time
- Error handling is important because API calls can fail (rate limits, invalid tickers, network issues)

## Important: Branch and PR
- Create branch: `7-plotly-chart-generation`
- Commit format: `type: description (#7)`
- PR body must include: `Closes #7`
- Follow existing code patterns (ruff formatting, type hints, docstrings)

## Expected Output
- Enhanced system prompt in `agent.py` with concrete chart patterns
- Tests verifying chart-related content
- All existing tests still passing
- PR created with `Closes #7` in body
