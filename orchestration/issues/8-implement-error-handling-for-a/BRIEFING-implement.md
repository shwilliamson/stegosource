# Agent Briefing: implement
Generated: 2026-02-16

## Your Task
Implement issue #8: Implement error handling for API limits, bad input, and agent failures

## Context
- Issue: #8 - Implement error handling for API limits, bad input, and agent failures
- Milestone: Milestone 2: Data Fetching & Visualization
- Dependencies: #6 (Alpha Vantage tool) and #7 (Chart generation) — both CLOSED
- Mode: all-issues

## Acceptance Criteria
- [ ] Invalid ticker: agent responds in chat with a helpful message ("That ticker doesn't exist. Did you mean X?")
- [ ] Rate limit hit: `st.toast()` notification ("Alpha Vantage rate limit reached. Try again later.")
- [ ] Missing API key: persistent `st.warning()` at the top of the main area ("Alpha Vantage API key not configured. Data features are unavailable.")
- [ ] Missing Anthropic API key: persistent `st.error()` explaining the agent cannot function without it
- [ ] Network errors: agent handles gracefully and reports in chat
- [ ] If the agent writes broken code to app.py and the hot-reload fails, the error is visible and recoverable

## Current State of the Codebase

### Error handling already in place:
1. **`tools/alpha_vantage.py`** already has clear error classes: `MissingApiKeyError`, `InvalidTickerError`, `RateLimitError`, `ApiError` — all subclass `AlphaVantageError`. These handle network errors, timeouts, HTTP errors, rate limits, and invalid tickers properly.

2. **`agent.py`** already has `AgentConfigError` (for missing Anthropic API key), `AgentQueryError` (for SDK errors), and `AgentError` (base). The `_validate_api_key()` function raises `AgentConfigError` when `ANTHROPIC_API_KEY` is not set.

3. **`app.py` scaffold** already catches `AgentConfigError`, `AgentError`, and generic `Exception` in the streaming response handler, showing `st.error()` messages.

### What needs to be added/changed:

1. **Missing Alpha Vantage API key warning**: At app startup (in the scaffold or just after it in the dynamic section), check if `ALPHAVANTAGE_API_KEY` is set. If not, show a persistent `st.warning()` at the top of the main area. This should be in the **scaffold section** since it's infrastructure-level. However, per the rules, the agent must NOT modify the scaffold. So place it right after `# === SCAFFOLD END ===` but before the dynamic section, OR add it as a persistent check at the top of the main area.

   **IMPORTANT**: Since the scaffold section cannot be modified by the dynamic agent, AND this is an infrastructure concern, you should add the API key check in the scaffold section of `app.py`. You ARE the developer agent, not the runtime agent, so you CAN and SHOULD edit the scaffold.

2. **Missing Anthropic API key error**: Similarly, check at startup if `ANTHROPIC_API_KEY` is set and show a persistent `st.error()`. The existing handler only fires when the user sends a message. We need a persistent banner at app startup.

3. **Agent system prompt updates**: The system prompt in `agent.py` should instruct the agent to:
   - Handle `InvalidTickerError` by suggesting similar tickers
   - Catch `RateLimitError` and use `st.toast()` instead of `st.error()`
   - Handle network errors gracefully in chat
   - Write valid Python and mentally test edits before saving

4. **Rate limit handling in app.py**: When the agent encounters a rate limit during execution, it should ideally use `st.toast()`. Since the agent runs tools via the SDK, this is best handled by instructing the agent via system prompt to use `st.toast()` for rate limits in the code it generates.

5. **Dynamic section error recovery**: Wrap the dynamic section execution in a try/except to catch errors from agent-generated code, making them visible and recoverable.

6. **Tests**: Add tests for:
   - Missing Alpha Vantage API key warning display
   - Missing Anthropic API key error display
   - System prompt contains error handling instructions
   - Dynamic section error recovery

## Architecture Decisions

### Where to place API key checks
- Place persistent API key warnings/errors **between the scaffold end and dynamic start** markers. These are infrastructure concerns that persist across reruns.
- Actually, place them in the scaffold section — you need to add them between the sidebar section and the SCAFFOLD END marker so they render in the main area. OR better: add them right after `# === SCAFFOLD END ===` but outside the dynamic markers. The area between scaffold end and dynamic start is effectively a "preamble" area.

### Actually recommended approach:
Add the API key checks **inside the scaffold section** right before `# === SCAFFOLD END ===`. This is correct because:
- These are infrastructure-level concerns
- They should always render regardless of what the agent puts in the dynamic section
- The scaffold is the right place for this (the "agent must not modify scaffold" rule applies to the runtime agent, not to us as developers)

### Error recovery for dynamic section
Wrap the dynamic section content execution in a try/except. Since Streamlit runs the entire file top-to-bottom, a crash in the dynamic section kills the whole app. By wrapping it, we can show a helpful error message while keeping the chat functional.

## Resources (Read as Needed)
- Issue details: `gh issue view 8`
- Current app.py, agent.py, tools/alpha_vantage.py — already described above
- Existing test files: `tests/test_app.py`, `tests/test_agent.py`, `tests/test_alpha_vantage.py`
- commands.md: `.claude/commands.md`

## Expected Output
- Working implementation matching acceptance criteria
- Tests passing
- PR created with "Closes #8" in body
- Branch name: `8-implement-error-handling`
