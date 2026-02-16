# Agent Briefing: implement
Generated: 2026-02-16

## Your Task
Implement issue #6: Implement Alpha Vantage API client as a custom agent tool

## Context
- This is a backend tool implementation (no UI work)
- Mode: all-issues (auto-merge handled by orchestrator)

## Acceptance Criteria
- [ ] `tools/alpha_vantage.py` implements an Alpha Vantage API client as a custom agent tool
- [ ] Tool supports fetching daily time series data for a given stock symbol
- [ ] Tool supports fetching intraday data at various intervals (5min, 15min, 30min, 60min)
- [ ] Tool returns structured data (dates, open, high, low, close, volume) suitable for charting
- [ ] API key loaded from `.env` (`ALPHAVANTAGE_API_KEY`)
- [ ] Clear error messages for: invalid ticker, rate limit hit (25/day), missing API key, network errors
- [ ] Tool registered with the agent so it can be invoked during conversation
- [ ] Data cached in session state to avoid redundant API calls for the same symbol/timeframe

## Technical Notes
- Alpha Vantage free tier: 25 requests/day, 5 requests/minute
- Use the `TIME_SERIES_DAILY` and `TIME_SERIES_INTRADAY` endpoints
- The custom tool should be defined as a function the agent can call via Bash or a helper module
- Return data as a list of dicts or pandas-compatible format for easy Plotly consumption
- `requests` library is already in pyproject.toml dependencies
- The agent uses `claude_agent_sdk` with `tools={"type": "preset", "preset": "claude_code"}` and `permission_mode="bypassPermissions"` — the agent invokes tools via Bash/Read/Write/Edit, so the Alpha Vantage tool should be a CLI script or importable module the agent can call from Bash
- The existing `tools/__init__.py` has a docstring indicating it's for custom tools

## Existing Code Patterns
- The project uses `python-dotenv` for env loading (already in agent.py)
- `tools/` package already exists with `__init__.py`
- Tests are in `tests/` with pytest + pytest-asyncio
- Use `ruff` for linting/formatting
- Type hints required throughout

## Important Constraints
- Do NOT modify anything in the scaffold section of app.py
- The agent system prompt in agent.py should be updated to mention the new tool is available
- The tool should be usable by the agent through its existing tool mechanism (Bash command or Python import)
- Session-level caching means using a simple in-memory cache (dict) within the module since the agent runs per-session

## Expected Output
- `tools/alpha_vantage.py` — Alpha Vantage API client with daily and intraday functions, caching, error handling
- `tests/test_alpha_vantage.py` — comprehensive unit tests with mocked HTTP responses
- Updated `agent.py` system prompt to inform the agent about the Alpha Vantage tool
- PR created with `Closes #6` in body
- Branch naming: `6-alpha-vantage-tool`
