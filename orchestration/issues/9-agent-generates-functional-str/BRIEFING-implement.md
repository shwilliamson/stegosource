# Agent Briefing: implement
Generated: 2026-02-16

## Your Task
Implement issue #9: Agent generates functional Streamlit forms and controls

## Context
- This is the Stegosource project - a self-modifying Streamlit data visualization app where an AI agent modifies `app.py` dynamically
- The agent already knows how to generate Plotly charts (issue #7, completed)
- Now the agent needs to also be able to generate Streamlit forms/widgets (date pickers, dropdowns, text inputs, multi-selects)
- Mode: all-issues (auto-merge handled by orchestrator)

## Acceptance Criteria
- [ ] Agent can write Streamlit form/widget code into app.py's dynamic section
- [ ] Date range pickers: `st.date_input()` for selecting start/end dates
- [ ] Dropdown selectors: `st.selectbox()` for chart type, time interval, etc.
- [ ] Text inputs: `st.text_input()` for stock symbol entry
- [ ] Multi-select: `st.multiselect()` for comparing multiple symbols
- [ ] Controls are functional after hot-reload -- user can interact with them
- [ ] Form interactions update the chart (e.g., changing the date range re-fetches data and re-renders)
- [ ] Agent can modify or remove existing controls when asked

## Technical Notes from Issue
- The agent writes real Streamlit widget code directly into app.py
- Widgets need `key` parameters for session state persistence across reruns
- Form submission pattern: use `st.form()` with `st.form_submit_button()` to batch widget inputs, or use individual widgets with callbacks
- The agent must write the logic that connects widgets to data fetching and chart updates -- this is self-contained in app.py
- Streamlit reruns the entire script when a widget value changes, so the code must handle current widget values gracefully

## What This Means In Practice
The work is about updating the **system prompt** in `agent.py` (the `SYSTEM_PROMPT` variable) to teach the Stegosource agent how to generate Streamlit forms and controls. This is the same pattern used for chart generation (issue #7) where instructions and examples were added to the system prompt.

Specifically, you need to:
1. Add a new section to the `SYSTEM_PROMPT` in `agent.py` that covers form/widget generation patterns
2. Include examples for: date range pickers, dropdown selectors, text inputs, multi-selects
3. Show how widgets connect to data fetching and chart rendering
4. Include guidance on `key` parameters for session state persistence
5. Include the `st.form()` / `st.form_submit_button()` pattern
6. Show how to modify or remove existing controls
7. Write comprehensive tests in `tests/test_agent.py` validating the system prompt contains the new sections
8. Ensure all existing tests still pass

## Patterns to Follow
- Look at the existing "Chart Generation Patterns" section in `SYSTEM_PROMPT` as a model
- Follow the same structure: section header, explanation, code examples, checklist
- The system prompt already references `from tools.alpha_vantage import fetch_daily` -- widget examples should use the same data fetching patterns
- Tests follow the `TestSystemPrompt` class pattern in `tests/test_agent.py`

## Resources (Read as Needed)
- Issue details: `gh issue view 9`
- Current system prompt: Read `agent.py` (the `SYSTEM_PROMPT` variable)
- Existing tests: Read `tests/test_agent.py`
- Chart theme: Read `chart_theme.py`
- Current app.py for dynamic section structure

## Expected Output
- Updated `agent.py` with comprehensive form/widget generation instructions in the system prompt
- Updated `tests/test_agent.py` with tests validating the new system prompt sections
- All tests passing (`pytest`)
- PR created with "Closes #9" in body
- Branch named `9-agent-generates-functional-streamlit-forms`
